# ONLY FOR GATHERING DATA, NOT USED IN RUNNING APPLICATION

import logging
import pandas as pd
from scapy.all import sniff
from scapy.layers.inet import IP


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


def capture_traffic(interface='en0', duration=30):
    logging.info(f"Using interface: {interface} for {duration} seconds.")
    packets = sniff(iface=interface, timeout=duration)
    logging.info(f"Intercepting done. Received {len(packets)} packets.")
    return packets


def process_data(packets):
    rows = []
    for packet in packets:
        if packet.haslayer(IP):
            packet_info = {
                'length': len(packet),
                'timestamp': packet.time,
                'source_ip': packet[IP].src,
                'destination_ip': packet[IP].dst,
                'protocol': packet[IP].proto
            }
            rows.append(packet_info)
    return pd.DataFrame(rows)


if __name__ == "__main__":
    print("Intercepting traffic...")
    captured_packets = capture_traffic()
    print("Processing data...")
    df = process_data(captured_packets)
    df.sort_values(by='timestamp', inplace=True)

    print("Saving data...")
    df.to_csv("model_data/captured_traffic.csv", index=False)
    print("Data saved into 'captured_traffic.csv'")
