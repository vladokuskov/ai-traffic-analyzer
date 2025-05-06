import pandas as pd
from matplotlib import pyplot as plt
import matplotlib.dates as mdates


def plot_detection_results(real_time_data, predicted_values, is_anomaly):
    """
    Plot real values, predicted values, and highlight anomalies.
    Assumes the index of `real_time_data` is datetime.
    """
    # Use the index as the timestamp
    real_time_data = real_time_data.copy()
    real_time_data['predicted'] = predicted_values
    real_time_data['is_anomaly'] = is_anomaly

    plt.figure(figsize=(14, 6))
    plt.plot(real_time_data.index, real_time_data['packet_length'], label='Real', color='blue')
    plt.plot(real_time_data.index, real_time_data['predicted'], label='Predicted', color='orange', linestyle='--')

    # Plot anomalies
    anomalies = real_time_data[real_time_data['is_anomaly']]
    if not anomalies.empty:
        plt.scatter(anomalies.index, anomalies['packet_length'], color='red', label='Anomaly', zorder=5)

    plt.xlabel('Time')
    plt.ylabel('Packet Length')
    plt.title('Real-Time Anomaly Detection')
    plt.legend()
    plt.grid(True)

    # Format x-axis as timeline
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    plt.gcf().autofmt_xdate()

    plt.tight_layout()
    plt.show()