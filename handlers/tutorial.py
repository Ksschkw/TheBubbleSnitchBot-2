from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler

async def tutorial_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["tutorial_step"] = 1
    text = (
        "👾 **Bubblemaps Bot Tutorial** 👾\n\n"
        "Step 1: **Token Scans & Favorites**\n"
        "• Send a token as `<chain> <address>` or just `<address>` (defaults to ETH).\n"
        "• Add tokens to your watchlist with /addfavorite.\n\n"
        "Hit **Next** to continue."
    )
    keyboard = [[InlineKeyboardButton("Next", callback_data="tutorial_next")]]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def tutorial_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    step = ctx.user_data.get("tutorial_step", 1)

    if query.data == "tutorial_next":
        step += 1
    elif query.data == "tutorial_back":
        step = max(1, step - 1)
    elif query.data == "tutorial_restart":
        step = 1

    ctx.user_data["tutorial_step"] = step

    if step == 1:
        text = (
            "👾 **Step 1: Token Scans & Favorites** 👾\n\n"
            "Send `<chain> <address>` or `<address>` (defaults to ETH).\n"
            "Save with /addfavorite to keep an eye on them! 💎"
        )
    elif step == 2:
        text = (
            "🔥 **Step 2: Trending & Updates** 🔥\n\n"
            "Check /trending to see which tokens are on fire by volume 📈.\n"
            "Favorites get real‑time alerts on big moves 🚨."
        )
    elif step == 3:
        text = (
            "📊 **Step 3: Bot Stats & More** 📊\n\n"
            "Use /stats for scan counts and performance 💰.\n"
            "Manage your watchlist with /removefavorite 🗑️."
        )
    elif step == 4:
        text = (
            "🔍 **Step 4: Token Analysis** 🔍\n\n"
            "After selecting a token, try these:\n"
            "• /tokendetails - Detailed token info\n"
            "• /topholders - Top token holders\n"
            "• /relatedtokens - Tokens linked to the current token"
        )
    else:
        text = (
            "🎉 **Tutorial Complete!** 🎉\n\n"
            "You've mastered token scans, favorites, trending checks, stats, and analysis.\n"
            "Type /tutorial anytime for a refresher. Keep rockin'! 🤘"
        )
        keyboard = [[InlineKeyboardButton("Restart Tutorial", callback_data="tutorial_restart")]]
        return await query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    buttons = []
    if step > 1:
        buttons.append(InlineKeyboardButton("Back", callback_data="tutorial_back"))
    buttons.append(InlineKeyboardButton("Next", callback_data="tutorial_next"))
    await query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup([buttons]), parse_mode="Markdown")


def register_tutorial(app):
    # In case you want to register dynamically instead of in bot.py
    app.add_handler(CommandHandler("tutorial", tutorial_start))
    app.add_handler(CallbackQueryHandler(tutorial_callback, pattern="^tutorial_"))
