import pandas as pd
from datetime import datetime
import time
import logging
from detector import load_or_train_model, real_time_anomaly_detection
from db import collection
from scapy.all import sniff
from scapy.layers.inet import IP


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def capture_traffic(interface='en0', duration=30):
    """
    Capture network traffic for a specified duration and return a list of packets.
    """
    logging.info(f"Using interface: {interface} for {duration} seconds.")
    packets = sniff(iface=interface, timeout=duration)
    logging.info(f"Intercepting done. Received {len(packets)} packets.")
    return packets


def process_data(packets):
    """
    Process captured packets and extract relevant data for anomaly detection.
    """
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


def run_detection(interface='en0', duration=30):
    """
    Run real-time anomaly detection using captured traffic.
    """
    # Capture real-time traffic
    captured_packets = capture_traffic(interface, duration)

    # Process the captured packets into a DataFrame
    real_time_data = process_data(captured_packets)

    # Load or train the ARIMA model
    model = load_or_train_model(real_time_data['length'])

    # Perform anomaly detection
    pred, real, err, err_pct = real_time_anomaly_detection(model, real_time_data)

    # Prepare document for MongoDB
    doc = {
        "timestamp": datetime.now(),
        "predicted": pred,
        "actual": real,
        "error": err,
        "error_pct": err_pct
    }

    # Save result to MongoDB
    collection.insert_one(doc)
    logging.info("Inserted anomaly result to DB")


def loop(interface='en0', duration=30):
    """
    Loop the detection every 60 seconds.
    """
    while True:
        run_detection(interface, duration)
        time.sleep(60)


if __name__ == "__main__":
    loop()
