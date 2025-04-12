import numpy as np
import pandas as pd
from pmdarima import auto_arima
import logging
import os
import joblib
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning, module='statsmodels')

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# Anomaly Detection Function
def detect_anomalies(df, window, confid_interval=2):
    df.fillna(0, inplace=True)
    df['error'] = df['length'] - df['predicted']
    df['error_pct'] = (df['error'] / df['predicted']) * 100
    df['err_meanval'] = df['error'].rolling(window=window).mean()
    df['err_deviation'] = df['error'].rolling(window=window).std()
    df['-lim'] = df['err_meanval'] - (confid_interval * df['err_deviation'])
    df['+lim'] = df['err_meanval'] + (confid_interval * df['err_deviation'])
    df['anomaly_points'] = np.where(
        (df['error'] > df['+lim']) | (df['error'] < df['-lim']),
        df['length'],
        np.nan
    )
    return df


# Real-Time Anomaly Detection with ARIMA
def real_time_anomaly_detection(model_arima, real_time_data, window=10, confid_interval=2):
    # Forecast the next value
    predicted = model_arima.predict(n_periods=1)

    predicted_value = int(predicted.iloc[0])

    # Get actual value from the last row
    real_value = real_time_data['length'].iloc[-1]
    # Calculate error
    error = real_value - predicted_value
    error_percentage = (error / predicted_value) * 100

    recent_window = real_time_data['length'].tail(window)

    std_dev = np.std(recent_window) if len(recent_window) > 1 else 0

    threshold = confid_interval * std_dev

    # Check if anomaly
    is_anomaly = False

    fallback_error_pct = 20

    if std_dev > 0:
        threshold = confid_interval * std_dev
        is_anomaly = abs(error) > threshold
    else:
        is_anomaly = abs(error_percentage) > fallback_error_pct
        threshold = f"{fallback_error_pct}% (fallback)"

    if is_anomaly:
        logging.warning(
            f"🚨 Anomaly detected! Predicted: {predicted_value:.2f}, Actual: {real_value}, Error: {error_percentage:.2f}%")
    else:
        logging.info(
            f"Real-time Data -> Predicted: {predicted_value:.2f}, Actual: {real_value}, Error: {error_percentage:.2f}%"
        )

    return predicted_value, real_value, error, error_percentage


# Load or Train ARIMA model
def load_or_train_model(series, model_path='model_data/model_arima.pkl'):
    if os.path.exists(model_path):
        logging.info("Loading existing ARIMA model...")
        model = joblib.load(model_path)
    else:
        logging.info("Training new ARIMA model...")
        model = auto_arima(series, start_p=1, max_p=5, start_q=1, max_q=5, seasonal=False, trace=True)
        joblib.dump(model, model_path)
        logging.info(f"Model saved to {model_path}")
    return model


# def main(csv_path, real_time_data, window=10, confid_interval=2):
#     # Load historical traffic data
#     captured_data = pd.read_csv(csv_path)
#     captured_data['timestamp'] = pd.to_datetime(captured_data['timestamp'], unit='s')
#     captured_data.set_index('timestamp', inplace=True)
#
#     # Load or train ARIMA model
#     model_arima = load_or_train_model(captured_data['length'])
#
#     # Real-Time Detection
#     predicted_value, real_value, error, error_percentage = real_time_anomaly_detection(
#         model_arima, real_time_data, window, confid_interval
#     )


# if __name__ == "__main__":
#     # Example real-time data
#     real_time_data_example = pd.DataFrame([{
#         'timestamp': pd.to_datetime(1743680205.474733, unit='s'),
#         'length': 300,
#         'source_ip': '192.168.0.102',
#         'destination_ip': '199.232.210.250',
#         'protocol': 3
#     }])
#
#     # Replace with your actual CSV path
#     captured_data_path = 'captured_traffic.csv'
#
#     main(captured_data_path, real_time_data_example)
