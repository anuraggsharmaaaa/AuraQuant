# ⚡ AuraQuant Terminal | Real-Time Market Telemetry & ML Risk Engine

An institutional-grade, real-time quantitative market telemetry dashboard and multi-asset ingestion engine built with Python, Docker, Streamlit, and scikit-learn. Designed to handle high-frequency WebSocket data streams, dynamic time-series resampling, and unsupervised machine learning anomaly detection.

![Python](https://img.shields.io/badge/Python-3.13-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-UI-FF4B4B.svg)
![Scikit-Learn](https://img.shields.io/badge/ML-Isolation_Forest-orange.svg)

---

## 🏗️ System Architecture & Telemetry Flow

AuraQuant is structured around a decoupled microservice architecture:

1. **Async Ingestion Engine (`src/ingestion/ticker.py`):** 
   - Utilizes a non-blocking `asyncio` event loop to connect to Binance combined WebSocket streams (`wss://stream.binance.com:9443`).
   - Simultaneously ingests real-time micro-ticks for multi-asset portfolios (`BTCUSDT`, `ETHUSDT`, `SOLUSDT`).
2. **Relational Persistence Layer (`src/database/`):** 
   - Built with SQLAlchemy ORM, managing thread-safe session commits to a local time-series SQLite database (`auraquant.db`).
3. **Quantitative & Machine Learning Analytics Engine (`src/utils/quant.py`):** 
   - Dynamically resamples raw tick data into customizable OHLCV candlesticks using Pandas.
   - Computes technical indicators including Volume Weighted Average Price (VWAP) and 2-Sigma Bollinger Bands.
   - **ML Anomaly Detection:** Deploys an unsupervised **Isolation Forest** model from `scikit-learn` trained dynamically on rolling returns, realized volatility, and aggregate volume to isolate structural market outliers.
4. **Institutional Dark-Mode Dashboard (`dashboard.py`):** 
   - Built with Streamlit, Plotly, and custom CSS styling.
   - Features a zero-flicker live rendering loop (`@st.fragment`), interactive tooltips (`i`), and dedicated real-time telemetry tabs.

---

## 🚀 Quick Start (Docker Deployment)

The entire infrastructure is fully containerized and orchestrated via Docker Compose, requiring zero local dependency configuration.

1. Clone the repository:
   ```zsh
   git clone [https://github.com/anuraggsharmaaaa/auraquant.git](https://github.com/anuraggsharmaaaa/auraquant.git)
   cd auraquant

   1. Spin up the containerized microservices (Ingestion Engine + Dashboard):
    docker compose up --build -d


   2. Access the live terminal in your browser:
    http://localhost:8501

   3. To stop the infrastructure:
    docker compose down

    
    
    🧪 Testing

The repository includes a comprehensive unit testing suite (pytest) to validate core mathematical functions (OHLCV resampling and VWAP accuracy):
    pytest tests/

🧮 Mathematical & ML Formulations

Bollinger Band Volatility Breach:

Upper Band = mu_{20} + 2\sigma_{20}, {Lower Band} = \mu_{20} - 2\sigma_{20}

Unsupervised Isolation Forest Outlier Detection:

Evaluates feature matrix X = [r_t, \sigma_5, V_t] (Returns, Volatility, Volume) to flag structural anomalies based on isolation depth across randomized decision trees.