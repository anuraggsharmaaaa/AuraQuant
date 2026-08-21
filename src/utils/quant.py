import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from src.database.connection import engine
from src.utils.logger import logger

def get_quant_metrics(symbol: str = "BTCUSDT", timeframe: str = "1min"):
    """
    Queries tick storage, aggregates OHLCV candlesticks, computes VWAP, 
    Bollinger Bands, and runs an Isolation Forest ML model for anomaly detection.
    """
    try:
        # 1. Fetch recent raw ticks for live feed
        raw_ticks = pd.read_sql(
            f"SELECT timestamp, symbol, price, volume FROM market_ticks WHERE symbol='{symbol}' ORDER BY id DESC LIMIT 15", 
            engine
        )
        
        # 2. Query full dataset for timeframe resampling
        df = pd.read_sql(f"SELECT timestamp, price, volume FROM market_ticks WHERE symbol='{symbol}'", engine)
        
        if df.empty or len(df) < 5:
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), {}

        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
        
        # 3. Resample into OHLCV Candles
        ohlcv = df.resample(timeframe).agg({
            'price': ['first', 'max', 'min', 'last'],
            'volume': 'sum'
        })
        ohlcv.columns = ['open', 'high', 'low', 'close', 'volume']
        ohlcv.dropna(inplace=True)
        
        # 4. Quantitative & Technical Indicators (Restoring Bollinger Bands for UI)
        ohlcv['vwap'] = (ohlcv['close'] * ohlcv['volume']).cumsum() / ohlcv['volume'].cumsum()
        ohlcv['sma_20'] = ohlcv['close'].rolling(window=20, min_periods=1).mean()
        ohlcv['std_20'] = ohlcv['close'].rolling(window=20, min_periods=1).std().fillna(0)
        
        # Bollinger Bands (2-Sigma) for chart rendering
        ohlcv['upper_band'] = ohlcv['sma_20'] + (ohlcv['std_20'] * 2)
        ohlcv['lower_band'] = ohlcv['sma_20'] - (ohlcv['std_20'] * 2)
        
        # 5. Machine Learning Feature Engineering & Anomaly Detection
        ohlcv['returns'] = ohlcv['close'].pct_change().fillna(0)
        ohlcv['volatility'] = ohlcv['close'].rolling(window=5, min_periods=1).std().fillna(0)
        
        features = ohlcv[['returns', 'volatility', 'volume']].copy()
        
        # Isolation Forest Unsupervised Outlier Detection (5% contamination)
        model = IsolationForest(contamination=0.05, random_state=42)
        preds = model.fit_predict(features)
        
        ohlcv['ml_anomaly'] = preds == -1
        ohlcv.reset_index(inplace=True)
        
        # Filter detected anomalies
        anomalies = ohlcv[ohlcv['ml_anomaly']].copy()
        
        # 6. Session Statistics
        latest_price = df['price'].iloc[-1]
        first_price = df['price'].iloc[0]
        price_change = latest_price - first_price
        pct_change = (price_change / first_price * 100) if first_price != 0 else 0.0
        
        stats = {
            "latest_price": latest_price,
            "price_change": price_change,
            "pct_change": pct_change,
            "high": df['price'].max(),
            "low": df['price'].min(),
            "total_volume": df['volume'].sum(),
            "tick_count": len(df),
            "anomaly_count": len(anomalies)
        }
        
        return ohlcv, raw_ticks, anomalies, stats
    except Exception as e:
        logger.error(f"Quant Engine Error: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), {}