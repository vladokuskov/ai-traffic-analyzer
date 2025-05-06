import pandas as pd
from datetime import datetime
import time
import logging

from scapy.config import conf
from scapy.interfaces import get_if_list

from app.plot import plot_detection_results
from detector import load_or_train_model, real_time_anomaly_detection
from db import collection
from scapy.all import sniff
from scapy.layers.inet import IP

# Configure logging for informational messages
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def detect_interface():
    """
    Automatically detect the best network interface for capturing traffic.
    This function checks available network interfaces and returns the one
    that matches the configuration or defaults to 'en0' if no match is found.
    """
    interfaces = get_if_list()
    for iface in interfaces:
        if conf.iface == iface:
            logging.info(f"Automatically selected interface: {iface}")
            return iface
    # Default to 'en0' if no other interface is found
    logging.info("No active interface found. Defaulting to 'en0'.")
    return 'en0'


def capture_traffic(interface=None, duration=30):
    """
    Capture network traffic for a specified duration and return a list of packets.
    This function either uses the provided interface or detects one automatically.
    It also logs the number of captured packets and the interface being used.
    """
    if interface is None:
        interface = detect_interface()

    logging.info(f"Using interface: {interface} for {duration} seconds.")
    packets = sniff(iface=interface, timeout=duration)
    logging.info(f"Intercepting done. Received {len(packets)} packets.")
    return packets


def process_data(packets, resample_interval='1S'):
    """
    Process captured packets and resample into time-based intervals.
    Returns a DataFrame with resampled statistics (mean packet length per second).
    """
    rows = []
    for packet in packets:
        if packet.haslayer(IP):
            packet_info = {
                'packet_length': len(packet),
                'timestamp': datetime.fromtimestamp(packet.time)  # Convert to datetime
            }
            rows.append(packet_info)

    df = pd.DataFrame(rows)
    if df.empty:
        return df

    df.set_index('timestamp', inplace=True)

    # Resample by the specified time interval (e.g., 1 second)
    resampled_df = df['packet_length'].resample(resample_interval).mean().fillna(0).to_frame()

    return resampled_df


def run_detection(interface, duration=30):
    """
    Run real-time anomaly detection using captured traffic.
    This function captures network traffic, processes the data into a DataFrame,
    loads or trains the ARIMA model, and performs anomaly detection.
    The results are saved to MongoDB.
    """
    # Capture real-time traffic
    captured_packets = capture_traffic(interface, duration)

    # Resample into 1-second intervals (mean packet length)
    real_time_data = process_data(captured_packets, resample_interval='1S')
    if real_time_data.empty or len(real_time_data) < 2:
        logging.warning("Not enough data for detection.")
        return

    # Load or train the ARIMA model
    model = load_or_train_model(real_time_data['packet_length'], 'model_data/model_arima.pkl')

    # Perform anomaly detection
    pred, real, err, err_pct, is_anomaly = real_time_anomaly_detection(model, real_time_data)

    # ONLY FOR DEBUG
    plot_detection_results(real_time_data, predicted_values=pred, is_anomaly=is_anomaly)

    # Prepare document for MongoDB, ensuring values are in native Python types
    doc = {
        "timestamp": datetime.now(),
        "predicted": int(pred),  # Ensure it's an int
        "actual": int(real),     # Ensure it's an int
        "error": int(err),       # Ensure it's an int
        "error_pct": float(err_pct)  # Ensure it's a float if it's a percentage
    }

    # Save result to MongoDB
    collection.insert_one(doc)
    logging.info("Inserted anomaly result to DB")


def loop(interface=None, duration=30):
    """
    Loop the detection every 60 seconds.
    This function runs the anomaly detection process in a continuous loop,
    capturing and analyzing network traffic every 60 seconds.
    """
    while True:
        run_detection(interface, duration)
        time.sleep(60)


if __name__ == "__main__":
    """ 
    Start the detection loop when the script is executed.
    This triggers the loop function to continuously detect anomalies.
    """
    loop()
