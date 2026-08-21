import asyncio
import json
import websockets
from datetime import datetime, timezone
from src.config import settings
from src.database.connection import SessionLocal, init_db
from src.database.models import MarketTick
from src.utils.logger import logger

async def stream_market_data():
    init_db()
    logger.info(f"Connecting to market stream: {settings.WEBSOCKET_URL}")
    
    while True:
        try:
            async with websockets.connect(settings.WEBSOCKET_URL) as ws:
                logger.info("WebSocket Connection Established. Ingesting live ticks...")
                
                while True:
                    raw_data = await ws.recv()
                    data = json.loads(raw_data)
                    
                    symbol = data.get("s", "UNKNOWN")
                    price = float(data.get("c", 0.0))
                    volume = float(data.get("v", 0.0))
                    
                    db = SessionLocal()
                    try:
                        tick = MarketTick(
                            symbol=symbol,
                            price=price,
                            volume=volume,
                            timestamp=datetime.now(timezone.utc)
                        )
                        db.add(tick)
                        db.commit()
                    except Exception as db_err:
                        db.rollback()
                        logger.error(f"Failed to write tick to database: {db_err}")
                    finally:
                        db.close()

                    logger.info(f"TICK PERSISTED | {symbol} | Price: ${price:,.2f} | Vol: {volume:,.4f}")
                    
        except websockets.exceptions.ConnectionClosed:
            logger.warning("WebSocket disconnected. Retrying connection in 5 seconds...")
            await asyncio.sleep(5)
        except asyncio.CancelledError:
            logger.info("Stream processing task cancelled.")
            break
        except Exception as e:
            logger.error(f"Unexpected stream error: {e}")
            await asyncio.sleep(5)

if __name__ == "__main__":
    try:
        asyncio.run(stream_market_data())
    except KeyboardInterrupt:
        logger.info("Pipeline shut down gracefully by user.")