#!/usr/bin/env python3
"""
agent_tools.py - Scapy-based network telemetry & incident diagnostic tool.
Used by the Autonomous SRE Network Investigator and Google ADK Agent.
"""

import sys
import json
from collections import defaultdict
from scapy.all import rdpcap, IP, TCP, Raw

def extract_sni_from_payload(payload: bytes) -> str | None:
    """Extract Server Name Indication (SNI) from TLS Client Hello payload."""
    try:
        # Check TLS Handshake record (0x16) and Client Hello (0x01)
        if len(payload) > 43 and payload[0] == 0x16 and payload[5] == 0x01:
            session_id_len = payload[43]
            pos = 44 + session_id_len
            if len(payload) > pos + 2:
                cipher_suites_len = int.from_bytes(payload[pos:pos+2], 'big')
                pos += 2 + cipher_suites_len
                if len(payload) > pos + 1:
                    compression_methods_len = payload[pos]
                    pos += 1 + compression_methods_len
                    if len(payload) > pos + 2:
                        extensions_len = int.from_bytes(payload[pos:pos+2], 'big')
                        pos += 2
                        end = pos + extensions_len
                        while pos + 4 <= min(end, len(payload)):
                            ext_type = int.from_bytes(payload[pos:pos+2], 'big')
                            ext_len = int.from_bytes(payload[pos+2:pos+4], 'big')
                            pos += 4
                            if ext_type == 0:  # server_name extension
                                if pos + 5 <= len(payload):
                                    server_name_len = int.from_bytes(payload[pos+3:pos+5], 'big')
                                    server_name = payload[pos+5:pos+5+server_name_len].decode('utf-8', errors='ignore')
                                    return server_name
                            pos += ext_len
    except Exception:
        pass
    return None

def inspect_pcap(pcap_path: str) -> dict:
    """Parses a pcap file using Scapy and returns flag statistics, TTL breakdown, and anomalies."""
    try:
        packets = rdpcap(pcap_path)
    except Exception as e:
        return {"error": f"Failed to read pcap: {str(e)}", "pcap_path": pcap_path}

    total_packets = len(packets)
    rst_count = 0
    dup_acks = 0
    ack_counts = defaultdict(int)
    endpoint_ttls = defaultdict(set)
    rst_packets = []
    flagged_sni = None
    packet_timeline = []

    for idx, pkt in enumerate(packets):
        if not pkt.haslayer(IP) or not pkt.haslayer(TCP):
            continue

        ip = pkt[IP]
        tcp = pkt[TCP]
        flags = tcp.sprintf('%TCP.flags%')
        ttl = ip.ttl
        endpoint_ttls[ip.src].add(ttl)

        event_desc = f"Packet #{idx+1}: {ip.src}:{tcp.sport} -> {ip.dst}:{tcp.dport} [{flags}] TTL={ttl}"
        packet_timeline.append(event_desc)

        # Track RST flags
        if 'R' in flags:
            rst_count += 1
            rst_packets.append({
                "packet_index": idx + 1,
                "src": ip.src,
                "dst": ip.dst,
                "sport": tcp.sport,
                "dport": tcp.dport,
                "ttl": ttl,
                "seq": tcp.seq,
                "ack": tcp.ack
            })

        # Track Duplicate ACKs
        if 'A' in flags and not ('S' in flags or 'F' in flags or 'R' in flags):
            if pkt.haslayer(Raw) and len(pkt[Raw].load) > 0:
                pass
            else:
                ack_key = (ip.src, ip.dst, tcp.sport, tcp.dport, tcp.ack)
                ack_counts[ack_key] += 1
                if ack_counts[ack_key] > 1:
                    dup_acks += 1

        # Check for TLS Client Hello SNI
        if pkt.haslayer(Raw):
            sni = extract_sni_from_payload(pkt[Raw].load)
            if sni:
                flagged_sni = sni

    # Anomaly Detection & Hypothesis Formulation
    anomalies = []
    ttl_anomalies = []

    # Check for TTL mismatch on RST packets vs normal endpoint traffic
    for rst in rst_packets:
        src = rst["src"]
        observed_ttl = rst["ttl"]
        normal_ttls = endpoint_ttls[src] - {observed_ttl}
        if normal_ttls:
            expected_ttl = next(iter(normal_ttls))
            anomaly_msg = (
                f"TCP RST from {src} has TTL={observed_ttl}, but legitimate packets from {src} "
                f"have TTL={expected_ttl}. Indicates an intermediate middlebox (firewall/DPI) injected this RST."
            )
            ttl_anomalies.append(anomaly_msg)
            anomalies.append({
                "type": "FIREWALL_RST_INJECTION",
                "severity": "CRITICAL",
                "evidence": anomaly_msg,
                "injected_rst": rst
            })

    if dup_acks > 3:
        anomalies.append({
            "type": "SEVERE_PACKET_LOSS_OR_MTU_BLACKHOLE",
            "severity": "HIGH",
            "evidence": f"Detected {dup_acks} duplicate ACKs."
        })

    if flagged_sni:
        anomalies.append({
            "type": "FLAGGED_TLS_SNI",
            "severity": "INFO",
            "evidence": f"TLS Client Hello contained SNI: {flagged_sni}"
        })

    report = {
        "pcap_file": pcap_path,
        "total_packets": total_packets,
        "rst_count": rst_count,
        "dup_acks": dup_acks,
        "endpoint_ttls": {ip: list(ttls) for ip, ttls in endpoint_ttls.items()},
        "rst_events": rst_packets,
        "ttl_anomalies": ttl_anomalies,
        "flagged_sni": flagged_sni,
        "anomalies": anomalies,
        "packet_timeline": packet_timeline
    }
    return report

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python agent_tools.py <path_to_pcap>")
        sys.exit(1)

    pcap_file = sys.argv[1]
    result = inspect_pcap(pcap_file)
    print(json.dumps(result, indent=2))
