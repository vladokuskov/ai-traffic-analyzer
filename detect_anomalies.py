import numpy as np
import pandas as pd
from pmdarima import auto_arima
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# Anomaly Detection Function
def detect_anomalies(df, window, confid_interval=2):
    df.fillna(0, inplace=True)
    df['error'] = df['length'] - df['predicted']
    df['error, %'] = (df['length'] - df['predicted']) / df['predicted'] * 100
    df['err_meanval'] = df['error'].rolling(window=window).mean()
    df['err_deviation'] = df['error'].rolling(window=window).std()
    df['-lim'] = df['err_meanval'] - (confid_interval * df['err_deviation'])
    df['+lim'] = df['err_meanval'] + (confid_interval * df['err_deviation'])
    df['anomaly_points'] = np.where(((df['error'] > df['+lim']) | (df['error'] < df['-lim'])), df['length'], np.nan)
    return df


# Real-Time Anomaly Detection with ARIMA
def real_time_anomaly_detection(model_arima, real_time_data, window=10, confid_interval=2):
    # Forecast the next value
    predicted_value = model_arima.predict(n_periods=1)[0]

    # Compare with the real-time data
    real_value = real_time_data['length'].iloc[-1]

    # Calculate error
    error = real_value - predicted_value
    error_percentage = (error / predicted_value) * 100

    # Detect anomaly if error is beyond threshold
    if abs(error) > confid_interval * np.std(real_time_data['length']):  # You can adjust the threshold here
        logging.warning(f"Anomaly detected! Predicted: {predicted_value}, Actual: {real_value}, Error: {error_percentage}%")

    # Return the predicted value
    return predicted_value, real_value, error, error_percentage


# Main Function to Train ARIMA and Process Real-Time Data
def main(csv_path, real_time_data, window=10, confid_interval=2):
    # Load the historical traffic data
    captured_data = pd.read_csv(csv_path)

    # Convert timestamp to datetime and set as index
    captured_data['timestamp'] = pd.to_datetime(captured_data['timestamp'], unit='s')
    captured_data.set_index('timestamp', inplace=True)

    # Train ARIMA model on captured traffic data (e.g., packet lengths)
    model_arima = auto_arima(captured_data['length'], start_p=1, max_p=5, start_q=1, max_q=5, seasonal=False, trace=True)

    # Real-Time Detection (can be placed in a loop if needed)
    predicted_value, real_value, error, error_percentage = real_time_anomaly_detection(model_arima, real_time_data, window, confid_interval)

    # Output result
    logging.info(f"Real-time Data -> Predicted: {predicted_value}, Actual: {real_value}, Error: {error_percentage}%")


if __name__ == "__main__":
    # Example usage for historical data and real-time data (replace these with actual paths)
    captured_data_path = 'captured_traffic.csv'  # Your historical traffic data CSV
    real_time_data_example = pd.DataFrame({
        'timestamp': pd.to_datetime(1743680205.474733, unit='s'),
        'length': 1600  # Example real-time packet data
    })

    # Run the main function
    main(captured_data_path, real_time_data_example)
