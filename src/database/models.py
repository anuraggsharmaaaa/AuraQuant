from sqlalchemy import Column, Integer, Float, String, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class MarketTick(Base):
    __tablename__ = "market_ticks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, index=True)
    price = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f"<MarketTick(symbol='{self.symbol}', price={self.price}, timestamp='{self.timestamp}')>"