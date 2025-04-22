import os, logging
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler

logging.basicConfig(level=logging.DEBUG)
load_dotenv()
app = Application.builder().token(os.getenv("TELEGRAM_TOKEN")).build()

async def hello(update, ctx):
    await update.message.reply_text("👋 Hello!")

app.add_handler(CommandHandler("hello", hello))
print(" Running minimal test bot…")
app.run_polling()
