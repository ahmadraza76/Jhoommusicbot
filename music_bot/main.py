import asyncio
from client import app, pytgcalls
from config import logger

async def main():
    try:
        await app.start()
        await pytgcalls.start()
        logger.info("Music Bot started successfully")
        await app.idle()
    except Exception as e:
        logger.error(f"Startup error: {e}")
    finally:
        await app.stop()
        await pytgcalls.stop()
        logger.info("Music Bot stopped")

if __name__ == "__main__":
    asyncio.run(main())
