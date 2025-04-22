import os
import datetime
import asyncio
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from core.cache import cleanup_cache
from core.playwright_sceenshot import init_browser, shutdown_browser
from handlers.commands import start_cmd, help_cmd, add_favorite, list_favorites, remove_favorite, trending, stats
from handlers.tutorial import tutorial_start, tutorial_callback, register_tutorial
from handlers.typos_and_messages import handle_contract_address, handle_typos

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    raise RuntimeError("Set TELEGRAM_TOKEN in .env")
print(f" Loaded token: {TOKEN[:4]}…{TOKEN[-4:]}")

def main():
    app = (
        Application.builder()
        .token(TOKEN)
        .post_init(init_browser)
        .post_shutdown(shutdown_browser)
        .concurrent_updates(False)
        .arbitrary_callback_data(True)
        .build()
    )

    # Core commands
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("addfavorite", add_favorite))
    app.add_handler(CommandHandler("favorites", list_favorites))
    app.add_handler(CommandHandler("removefavorite", remove_favorite))
    app.add_handler(CommandHandler("trending", trending))
    app.add_handler(CommandHandler("stats", stats))

    # Tutorial flow
    app.add_handler(CommandHandler("tutorial", tutorial_start))
    app.add_handler(CallbackQueryHandler(tutorial_callback, pattern="^tutorial_"))
    register_tutorial(app)

    # Messages: catch token scans and typos
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_contract_address))
    app.add_handler(MessageHandler(filters.COMMAND, handle_typos))

    # Scheduled cache cleanup
    app.job_queue.run_repeating(cleanup_cache, interval=int(os.getenv("CACHE_EXPIRY", 300)))

    print("Bot is running…")
    app.run_polling()

if __name__ == "__main__":
    main()
