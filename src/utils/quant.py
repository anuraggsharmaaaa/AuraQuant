import pandas as pd
import numpy as np
from src.database.connection import engine
from src.utils.logger import logger

# Added 'symbol' parameter to make it dynamic
def get_quant_metrics(symbol: str = "BTCUSDT", timeframe: str = "1min"):
    """
    Queries tick storage, aggregates OHLCV candlesticks, 
    computes VWAP, SMA, Bollinger Bands, and detects statistical anomalies.
    """
    try:
        # Update query to filter by selected symbol
        raw_ticks = pd.read_sql(
            f"SELECT timestamp, symbol, price, volume FROM market_ticks WHERE symbol='{symbol}' ORDER BY id DESC LIMIT 15", 
            engine
        )
        
        # Update query to filter by selected symbol
        df = pd.read_sql(f"SELECT timestamp, price, volume FROM market_ticks WHERE symbol='{symbol}'", engine)
        
        if df.empty:
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), {}

        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
        
        ohlcv = df.resample(timeframe).agg({
            'price': ['first', 'max', 'min', 'last'],
            'volume': 'sum'
        })
        ohlcv.columns = ['open', 'high', 'low', 'close', 'volume']
        ohlcv.dropna(inplace=True)
        
        ohlcv['vwap'] = (ohlcv['close'] * ohlcv['volume']).cumsum() / ohlcv['volume'].cumsum()
        ohlcv['sma_5'] = ohlcv['close'].rolling(window=5, min_periods=1).mean()
        ohlcv['sma_20'] = ohlcv['close'].rolling(window=20, min_periods=1).mean()
        ohlcv['std_20'] = ohlcv['close'].rolling(window=20, min_periods=1).std().fillna(0)
        ohlcv['upper_band'] = ohlcv['sma_20'] + (ohlcv['std_20'] * 2)
        ohlcv['lower_band'] = ohlcv['sma_20'] - (ohlcv['std_20'] * 2)
        ohlcv['vol_sma_10'] = ohlcv['volume'].rolling(window=10, min_periods=1).mean()
        
        ohlcv['price_anomaly'] = (ohlcv['close'] > ohlcv['upper_band']) | (ohlcv['close'] < ohlcv['lower_band'])
        ohlcv['volume_anomaly'] = (ohlcv['volume'] > (ohlcv['vol_sma_10'] * 3)) & (ohlcv['vol_sma_10'] > 0)
        
        ohlcv.reset_index(inplace=True)
        
        anomalies = ohlcv[ohlcv['price_anomaly'] | ohlcv['volume_anomaly']].copy()
        
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