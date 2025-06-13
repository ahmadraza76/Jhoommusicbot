import asyncio
import sys
import os

# Add music_bot directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'music_bot'))

from music_bot.client import app, pytgcalls
from music_bot.config import logger

# Import all command handlers
import music_bot.start_command
import music_bot.playback_commands
import music_bot.control_commands
import music_bot.auth_commands
import music_bot.broadcast_command
import music_bot.callback_handlers

async def main():
    try:
        logger.info("Starting Music Bot...")
        await app.start()
        await pytgcalls.start()
        logger.info("Music Bot started successfully!")
        logger.info("Bot is now running. Press Ctrl+C to stop.")
        await app.idle()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Startup error: {e}")
    finally:
        try:
            await pytgcalls.stop()
            await app.stop()
            logger.info("Music Bot stopped gracefully")
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

if __name__ == "__main__":
    asyncio.run(main())