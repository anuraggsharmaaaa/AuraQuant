import pandas as pd
import numpy as np

def test_ohlcv_resampling():
    """Validates that raw ticks correctly aggregate into OHLCV candles."""
    # Create fake tick data
    data = {
        'timestamp': pd.date_range(start='1/1/2026', periods=4, freq='15s'),
        'price': [100.0, 105.0, 95.0, 102.0],
        'volume': [1.0, 2.0, 1.0, 2.0]
    }
    df = pd.DataFrame(data)
    df.set_index('timestamp', inplace=True)
    
    # Resample to 1-minute candle
    ohlcv = df.resample('1min').agg({
        'price': ['first', 'max', 'min', 'last'],
        'volume': 'sum'
    })
    ohlcv.columns = ['open', 'high', 'low', 'close', 'volume']
    
    # Assert mathematical accuracy
    assert ohlcv['open'].iloc[0] == 100.0
    assert ohlcv['high'].iloc[0] == 105.0
    assert ohlcv['low'].iloc[0] == 95.0
    assert ohlcv['close'].iloc[0] == 102.0
    assert ohlcv['volume'].iloc[0] == 6.0

def test_vwap_calculation():
    """Validates the Volume Weighted Average Price (VWAP) math."""
    data = {
        'close': [100.0, 110.0],
        'volume': [10.0, 20.0]
    }
    df = pd.DataFrame(data)
    
    # VWAP = ((100 * 10) + (110 * 20)) / (10 + 20) = 3200 / 30 = 106.66...
    df['vwap'] = (df['close'] * df['volume']).cumsum() / df['volume'].cumsum()
    
    assert np.isclose(df['vwap'].iloc[-1], 106.666, atol=0.01)