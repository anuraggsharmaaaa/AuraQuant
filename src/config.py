import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "AuraQuant Telemetry"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./data/auraquant.db")
    # Free tier crypto market stream (no API key required to test pipeline)
    WEBSOCKET_URL: str = os.getenv("WEBSOCKET_URL", "wss://stream.binance.com:9443/ws/btcusdt@ticker")

settings = Settings()