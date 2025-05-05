import numpy as np
import pandas as pd
from pmdarima import auto_arima
import logging
import os
import joblib
import warnings

# Suppress specific warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning, module='statsmodels')

# Set up logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# Real-Time Anomaly Detection with ARIMA
def real_time_anomaly_detection(model_arima, real_time_data, window=10, confid_interval=2):
    """
    Perform real-time anomaly detection using a trained ARIMA model.
    It compares the predicted value with the actual value and checks if the error exceeds the threshold.
    Arguments:
    model_arima -- The trained ARIMA model used for predictions.
    real_time_data -- The real-time data for anomaly detection.
    window -- The rolling window size used for calculating standard deviation.
    confid_interval -- The confidence interval used to determine the anomaly threshold.

    Returns:
    predicted_value -- The predicted value for the next period.
    real_value -- The actual value from the real-time data.
    error -- The error between predicted and actual values.
    error_percentage -- The percentage error between predicted and actual values.
    """
    # Forecast the next value
    predicted = model_arima.predict(n_periods=1)
    predicted_value = int(predicted.iloc[0])  # Get the predicted value

    # Get actual value from the last row
    real_value = real_time_data['length'].iloc[-1]
    error = real_value - predicted_value  # Calculate error
    error_percentage = (error / predicted_value) * 100  # Calculate error percentage

    recent_window = real_time_data['length'].tail(window)  # Get the most recent data

    std_dev = np.std(recent_window) if len(recent_window) > 1 else 0  # Calculate standard deviation

    threshold = confid_interval * std_dev  # Calculate the threshold based on standard deviation

    # Check if anomaly
    is_anomaly = False

    fallback_error_pct = 20  # Fallback percentage if standard deviation is zero

    if std_dev > 0:
        # If standard deviation is greater than 0, use it for thresholding
        is_anomaly = abs(error) > threshold
    else:
        # If no standard deviation, fallback to using error percentage threshold
        is_anomaly = abs(error_percentage) > fallback_error_pct
        threshold = f"{fallback_error_pct}% (fallback)"

    if is_anomaly:
        logging.warning(
            f"🚨 Anomaly detected! Predicted: {predicted_value:.2f}, Actual: {real_value}, Error: {error_percentage:.2f}%")
    else:
        logging.info(
            f"Real-time Data -> Predicted: {predicted_value:.2f}, Actual: {real_value}, Error: {error_percentage:.2f}%"
        )

    return predicted_value, real_value, error, error_percentage, is_anomaly


# Load or Train ARIMA model
def load_or_train_model(series, model_path='app/model_data/model_arima.pkl'):
    """
    Load an existing ARIMA model from a file, or train a new model if one doesn't exist.
    The trained model is saved for future use.
    Arguments:
    series -- The time series data used to train the ARIMA model.
    model_path -- The path where the ARIMA model is stored or saved.

    Returns:
    model -- The trained ARIMA model.
    """
    if os.path.exists(model_path):
        logging.info("Loading existing ARIMA model...")
        model = joblib.load(model_path)  # Load the model from file
    else:
        logging.info("Training new ARIMA model...")
        model = auto_arima(series, start_p=1, max_p=5, start_q=1, max_q=5, seasonal=False, trace=True)  # Train a new model
        joblib.dump(model, model_path)  # Save the model for future use
        logging.info(f"Model saved to {model_path}")
    return model

# NOT USED

# Anomaly Detection Function
# def detect_anomalies(df, window, confid_interval=2):
#     """
#     Detect anomalies in the given DataFrame based on predicted vs actual values.
#     It calculates error and sets thresholds for anomaly detection based on a rolling window of errors.
#     Arguments:
#     df -- The DataFrame containing the actual and predicted data.
#     window -- The rolling window size for calculating error metrics.
#     confid_interval -- The confidence interval used to set the anomaly detection threshold.
#
#     Returns:
#     The modified DataFrame with anomaly detection results.
#     """
#     df.fillna(0, inplace=True)  # Fill NaN values with 0
#     df['error'] = df['length'] - df['predicted']  # Calculate error (actual - predicted)
#     df['error_pct'] = (df['error'] / df['predicted']) * 100  # Calculate error percentage
#     df['err_meanval'] = df['error'].rolling(window=window).mean()  # Rolling mean of errors
#     df['err_deviation'] = df['error'].rolling(window=window).std()  # Rolling standard deviation of errors
#     df['-lim'] = df['err_meanval'] - (confid_interval * df['err_deviation'])  # Lower limit for anomaly
#     df['+lim'] = df['err_meanval'] + (confid_interval * df['err_deviation'])  # Upper limit for anomaly
#     df['anomaly_points'] = np.where(
#         (df['error'] > df['+lim']) | (df['error'] < df['-lim']),
#         df['length'],
#         np.nan
#     )  # Mark points as anomalies if outside the limits
#     return df

# USED FOR GATHERING DATA FOR MODEL TRAINING
#
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
