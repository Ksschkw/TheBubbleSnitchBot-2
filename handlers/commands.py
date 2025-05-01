import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import ContextTypes
from core.api_clients import fetch_bubble, fetch_meta, fetch_market
from core.playwright_sceenshot import generate_screenshot
from core.extra import (
    update_global_on_add,
    update_global_on_remove,
    get_stats,
    GLOBAL_FAVS,
)

# which chains we support
SUPPORTED_CHAINS = {"eth", "bsc", "ftm", "avax", "cro", "arbi", "poly", "base", "sol"}


async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚀 Welcome to BubbleMaps Bot! 🚀\n\n"
        "Your ultimate crypto assistant: scan tokens, manage favorites, get live updates, and more.\n"
        "Type /tutorial for a guided tour or /help for the quick rundown."
    )


# async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     await update.message.reply_text(
#         "🤖 **Help Menu** 🤖\n\n"
#         "• /start - Welcome message\n"
#         "• /tutorial - Step-by-step guided tour\n"
#         "• /addfavorite <chain> <address> - Add a token to your watchlist\n"
#         "• /favorites - List your saved tokens\n"
#         "• /removefavorite <chain> <address> - Remove a token from favorites\n"
#         "• /trending - See top trending tokens by volume\n"
#         "• /stats - Check bot statistics",
#         parse_mode="Markdown"
#     )
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 **Help Menu** 🤖\n\n"
        "• /start - Welcome message\n"
        "• /tutorial - Step-by-step guided tour\n"
        "• /addfavorite <chain> <address> - Add a token to your watchlist\n"
        "• /favorites - List your saved tokens\n"
        "• /removefavorite <chain> <address> - Remove a token from favorites\n"
        "• /trending - See top trending tokens by volume\n"
        "• /stats - Check bot statistics\n"
        "• /relatedtokens - View tokens related to the current token",
        parse_mode="Markdown"
    )


async def add_favorite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    parts = update.message.text.strip().split()
    if len(parts) != 3:
        return await update.message.reply_text("Usage: /addfavorite <chain> <address>")

    _, chain, address = parts
    chain = chain.lower()
    if chain not in SUPPORTED_CHAINS:
        return await update.message.reply_text(f"Unsupported chain. Supported: {', '.join(SUPPORTED_CHAINS)}")

    # simple EVM‐style check for non‐Solana chains
    if chain != "sol" and not (address.startswith("0x") and len(address) == 42):
        return await update.message.reply_text("Invalid address format for this chain.")

    favorites = context.user_data.get("favorites", [])
    token = {"chain": chain, "address": address}
    if token in favorites:
        return await update.message.reply_text("Token is already in your favorites.")

    favorites.append(token)
    context.user_data["favorites"] = favorites
    update_global_on_add(chain, address)
    await update.message.reply_text("Token added to favorites! ❤️")


async def list_favorites(update: Update, context: ContextTypes.DEFAULT_TYPE):
    favorites = context.user_data.get("favorites", [])
    if not favorites:
        return await update.message.reply_text("You have no favorite tokens. Use /addfavorite to add one. 🤍")

    lines = ["Your favorite tokens:"]
    for t in favorites:
        url = f"https://app.bubblemaps.io/{t['chain']}/token/{t['address']}"
        lines.append(f"{t['chain'].upper()} - [{t['address'][-6:]}]({url})")

    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


async def remove_favorite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    parts = update.message.text.strip().split()
    if len(parts) != 3:
        return await update.message.reply_text("Usage: /removefavorite <chain> <address>")

    _, chain, address = parts
    chain = chain.lower()
    if chain not in SUPPORTED_CHAINS:
        return await update.message.reply_text(f"Unsupported chain. Supported: {', '.join(SUPPORTED_CHAINS)}")

    if chain != "sol" and not (address.startswith("0x") and len(address) == 42):
        return await update.message.reply_text("Invalid address format for this chain.")

    favorites = context.user_data.get("favorites", [])
    token = {"chain": chain, "address": address}
    if token not in favorites:
        return await update.message.reply_text("Token not found in your favorites.")

    favorites.remove(token)
    context.user_data["favorites"] = favorites
    update_global_on_remove(chain, address)
    await update.message.reply_text("Token removed from your favorites. 💔")


async def trending(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not GLOBAL_FAVS:
        return await update.message.reply_text(
            "No tokens in global favorites yet. Add some tokens to watch the trending list! 🔥"
        )

# bubble = await fetch_bubble(chain, address)
# name = bubble.get("full_name", "N/A")
    data = []
    for (chain, addr), _count in GLOBAL_FAVS.items():
        bubble = await fetch_bubble(chain, addr)
        name = bubble.get("full_name", "N/A")
        md = await fetch_market(chain, addr)
        if md:
            data.append({"chain": chain, "name":name, "address": addr, "vol": md.get("vol", 0), "price": md.get("price", 0)})

    if not data:
        return await update.message.reply_text("No valid market data available for trending tokens.")

    data.sort(key=lambda x: float(x["vol"] or 0), reverse=True)
    lines = ["🔥 **Trending Tokens (by volume)** 🔥"]
    for i, t in enumerate(data[:5], start=1):
        url = f"https://app.bubblemaps.io/{t['chain']}/token/{t['address']}"
        lines.append(f"{i}. {t['chain'].upper()} -{t['name']}– Volume: ${t['vol']} – Price: ${t['price']} – [View Map]({url})")

    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    favs = context.user_data.get("favorites", [])
    msg = get_stats(favs)
    await update.message.reply_text(msg, parse_mode="Markdown")
