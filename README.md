# Bachelor Diploma Project - Real-Time Anomaly Detection in Network Traffic

## Overview

This project is a **Bachelor Diploma Project** aimed at creating a real-time anomaly detection system for network traffic using machine learning. The system leverages **ARIMA (AutoRegressive Integrated Moving Average)** models to predict traffic patterns and identify anomalies in real-time. It captures network traffic, processes the data, applies the ARIMA model for prediction, and then performs anomaly detection by comparing the predicted traffic to actual values.

## Project Structure

The system is designed to work in real-time, using live network traffic data to detect anomalies. The project is structured in several key modules:

- **Traffic Capture**: Uses the `scapy` library to sniff and capture network traffic.
- **Data Processing**: Processes captured packets and extracts features for anomaly detection.
- **Anomaly Detection**: The core of the project, it uses ARIMA models to predict normal traffic patterns and detect anomalies based on prediction errors.
- **Database Integration**: Captures the results and stores them in a MongoDB database for future analysis.
- **API Interface**: Exposes a REST API using **FastAPI** to query stored anomaly data and access real-time detection results.
- **Model Training & Saving**: ARIMA models are either trained from scratch or loaded from pre-saved models, ensuring continuous learning and adaptation to network traffic changes.

## Technologies Used

- **Python**: The primary programming language used for data processing, anomaly detection, and API development.
- **Scapy**: A Python library used to capture network traffic.
- **ARIMA (from pmdarima)**: Used for time-series forecasting and anomaly detection.
- **MongoDB**: A NoSQL database used for storing anomaly detection results.
- **FastAPI**: A modern, fast (high-performance) web framework for building APIs with Python.
- **Joblib**: For saving and loading trained ARIMA models.
- **Docker**: Used to containerize the application for easy deployment and scaling.

## Functionality

### 1. **Traffic Capture**
The system uses `scapy` to capture network traffic from a specified network interface. The traffic is then processed to extract relevant features such as the length of the packets, source IP, destination IP, and protocol type.

### 2. **Anomaly Detection**
The captured network data is processed to calculate errors between predicted and actual traffic values. ARIMA models are used to forecast the expected traffic pattern, and anomalies are detected when the error exceeds certain thresholds.

### 3. **API Endpoints**
The project provides the following REST API endpoints:
- **`GET /anomalies`**: Retrieves all detected anomalies from the database.
- **`GET /anomalies/latest`**: Retrieves the most recent anomaly detected.

### 4. **Database Storage**
Anomalies detected are stored in a MongoDB database, which allows for efficient querying and future analysis of detected anomalies.

## Setup & Installation

### Prerequisites
- Python 3.11+
- MongoDB running locally or via a cloud provider (configured in `.env`)
- Docker (for containerization)

### Installation Steps

1. Clone the repository:
    ```bash
    git clone https://github.com/vladokuskov/ai-traffic-analyzer.git
    cd ai-traffic-analyzer
    ```

2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Set up MongoDB connection:
    - Ensure MongoDB is running locally or set up a cloud instance.
    - Update the `MONGO_URI` in your `.env` file if necessary:
      ```
      MONGO_URI=mongodb://localhost:27017/
      ```

4. Run the FastAPI application:
    ```bash
    uvicorn app.main:app --reload
    ```

5. Optionally, if you want to run the project in a Docker container:
    - Build the Docker image:
      ```bash
      docker build -t ai-traffic-analyzer .
      ```
    - Run the Docker container:
      ```bash
      docker run -p 8000:8000 ai-traffic-analyzer
      ```

## How It Works

- **Capture Traffic**: The system starts by capturing live network traffic from the specified interface using `scapy`.
- **Process Data**: Once the data is captured, it is processed to extract meaningful features like packet length, source and destination IPs, and protocol.
- **ARIMA Model**: The system uses an ARIMA model to predict the traffic pattern. The model can be trained from scratch or use a pre-trained model if available.
- **Anomaly Detection**: The system compares the predicted traffic values with the actual traffic and flags any large discrepancies as anomalies.
- **Database**: The anomaly detection results are then saved into a MongoDB database, where they can be queried via a REST API.
- **Real-Time Monitoring**: The application continuously monitors network traffic, detects anomalies, and stores the results for further analysis.

To collect data for training the ARIMA model and real-time anomaly detection, you will need to capture network traffic. This is done using the `scapy` library, which allows for packet sniffing on a specified network interface.

The `capture_traffic.py` file captures network traffic, processes the packets, and extracts relevant features such as:
- Packet length
- Source and destination IP
- Protocol

Here's how you can collect data:

1. Open the `capture_traffic.py` file.
2. The script uses `scapy`'s `sniff()` function to capture packets for a specified duration. You can modify the `duration` parameter in the `capture_traffic()` function to control how long data is collected.
3. The captured packets are processed into a Pandas DataFrame for further use.
