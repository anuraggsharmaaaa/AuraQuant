import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "AuraQuant Telemetry"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./data/auraquant.db")
    # Combined WebSocket stream for BTC, ETH, and SOL
    WEBSOCKET_URL: str = os.getenv("WEBSOCKET_URL", "wss://stream.binance.com:9443/stream?streams=btcusdt@ticker/ethusdt@ticker/solusdt@ticker")

settings = Settings()