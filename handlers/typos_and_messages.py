# handlers/typos_and_messages.py

import os
from difflib import get_close_matches
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from core.api_clients import fetch_bubble, fetch_meta, fetch_market
from core.playwright_sceenshot import generate_screenshot
from core.extra import increment_scans, compute_risk

# simple typo‐to‐command map
CMD_SUGGEST = {
    # /start variants
    'start': '/start', 'begin': '/start', 'init': '/start', 'boot': '/start',
    'welcome': '/start', 'launch': '/start', 'onboard': '/start', 'hello': '/start',
    'hi': '/start', 'hey': '/start', 'greet': '/start', 'crypto': '/start',
    'bubblemaps': '/start', 'bubbles': '/start', 'maps': '/start', 'bot': '/start',
    'assistant': '/start', 'yo': '/start', 'sup': '/start', 'holla': '/start',
    'salute': '/start', 'bro': '/start', 'dude': '/start', 'sister': '/start',
    'sibling': '/start', 'friend': '/start', 'partner': '/start', 'compadre': '/start',

    # /help variants
    'help': '/help', 'halp': '/help', 'assist': '/help', 'support': '/help',
    'commands': '/help', 'faq': '/help', 'info': '/help', 'question': '/help',
    'query': '/help', 'manual': '/help', 'howto': '/help', 'instructions': '/help',
    'directions': '/help', 'tips': '/help', 'advice': '/help', 'hints': '/help',
    'knowledge': '/help', 'resources': '/help', 'assistance': '/help', 'aide': '/help',
    'guidance': '/help', 'coaching': '/help', 'mentoring': '/help',

    # /tutorial variants
    'tutorial': '/tutorial', 'tut': '/tutorial', 'tour': '/tutorial', 'demo': '/tutorial',
    'walkthrough': '/tutorial', 'showcase': '/tutorial', 'explore': '/tutorial',
    'overview': '/tutorial', 'introduction': '/tutorial', 'orientation': '/tutorial',
    'briefing': '/tutorial', 'presentation': '/tutorial', 'show': '/tutorial',
    'exhibit': '/tutorial', 'exposition': '/tutorial', 'explanation': '/tutorial',
    'insight': '/tutorial', 'reveal': '/tutorial', 'unveil': '/tutorial',
    'demonstration': '/tutorial', 'show-and-tell': '/tutorial', 'uncover': '/tutorial',
    'expose': '/tutorial', 'display': '/tutorial',

    # /addfavorite variants
    'addfavorite': '/addfavorite', 'addfav': '/addfavorite', 'favadd': '/addfavorite',
    'favorite': '/addfavorite', 'favourite': '/addfavorite', 'add': '/addfavorite',
    'addtoken': '/addfavorite', 'addtokenfavorite': '/addfavorite', 'addtokenfav': '/addfavorite',
    'addtokenfavourite': '/addfavorite', 'addtok': '/addfavorite', 'addtokfav': '/addfavorite',

    # /favorites variants
    'favorites': '/favorites', 'fav': '/favorites', 'favlist': '/favorites',
    'favourites': '/favorites', 'love': '/favorites', 'dub': '/favorites', 'mine': '/favorites',

    # /removefavorite variants
    'removefavorite': '/removefavorite', 'remfavorite': '/removefavorite', 'rmfav': '/removefavorite',
    'deletefavorite': '/removefavorite', 'delfavorite': '/removefavorite', 'unfavorite': '/removefavorite',
    'unfav': '/removefavorite', 'del': '/removefavorite', 'rm': '/removefavorite',
    'delete': '/removefavorite', 'remove': '/removefavorite',

    # /trending variants
    'trending': '/trending', 'trend': '/trending', 'hot': '/trending', 'top': '/trending',

    # /stats variants
    'stats': '/stats', 'statistics': '/stats', 'data': '/stats', 'metrics': '/stats'
}

SUPPORTED_CHAINS = {"eth", "bsc", "ftm", "avax", "cro", "arbi", "poly", "base", "sol"}


def validate_address(chain: str, address: str) -> bool:
    if chain in {"eth", "bsc", "ftm", "avax", "cro", "arbi", "poly", "base"}:
        return address.startswith("0x") and len(address) == 42
    return True


async def handle_typos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""
    cmd = text.lower().split()[0]
    if cmd.startswith("/"):
        cmd = cmd[1:]
    match = get_close_matches(cmd, CMD_SUGGEST.keys(), n=1, cutoff=0.7)
    if match:
        suggestion = CMD_SUGGEST[match[0]]
        await update.message.reply_text(
            f"❌ Unrecognized command: `/{cmd}`\n"
            f"💡 Did you mean **{suggestion}**?\n"
            f"Try: `{suggestion} <parameters>`\n\n"
            "📋 List all commands with `/start`",
            parse_mode="Markdown",
        )
    else:
        await update.message.reply_text("🤖 I don't recognize that command. Type `/start` to see available commands.")


async def handle_contract_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    parts = update.message.text.strip().split()
    if len(parts) not in (1, 2):
        return await update.message.reply_text(
            "Invalid format. Use: `<chain> <address>` or `<address>` (defaults to ETH)."
        )

    # parse chain/address
    if len(parts) == 1:
        chain, address = "eth", parts[0]
    else:
        chain, address = parts[0].lower(), parts[1]

    if chain not in SUPPORTED_CHAINS:
        return await update.message.reply_text(
            f"Unsupported chain. Supported: {', '.join(SUPPORTED_CHAINS)}"
        )
    if not validate_address(chain, address):
        return await update.message.reply_text("Invalid address format for this chain.")

    # fetch data
    bubble = await fetch_bubble(chain, address)
    meta = await fetch_meta(chain, address)
    market = await fetch_market(chain, address)

    if not bubble or not meta:
        return await update.message.reply_text("Error fetching data. Token may not be supported.")

    # screenshot
    screenshot = await generate_screenshot(chain, address, context)
    if not screenshot:
        return await update.message.reply_text("Failed to generate map.")

    # build caption
    name = bubble.get("full_name", "N/A")
    sym = bubble.get("symbol", "N/A")
    score = meta.get("score", "N/A")
    cex_pct = meta.get("cex", "N/A")
    contract_pct = meta.get("contract", "N/A")
    price = market.get("price", "N/A") if market else "N/A"
    cap = market.get("cap", "N/A") if market else "N/A"
    vol = market.get("vol", "N/A") if market else "N/A"

    # compute risk
    try:
        _score = float(score)
        _vol = float(vol)
        _cex = float(cex_pct)
        _contract = float(contract_pct)
    except Exception:
        _score = _vol = _cex = _contract = 0
    risk = compute_risk(_score, _vol, _cex, _contract)

    caption = (
        f"🔍 **SUPPLY ANALYSIS** 🔍\n\n"
        f"**Token**: {name} ({sym}) 💎\n"
        f"**Chain**: {chain.upper()} 🔗\n"
        f"**Decentralization Score**: {score}/100 ⭐\n"
        f"**Identified Supply**:\n {cex_pct}% in CEX 🏦 ,\n {contract_pct}% in Contracts 📜\n\n"
        f"**Price**: ${price} 💲\n"
        f"**Market Cap**: ${cap} 💰\n"
        f"**Volume**: ${vol} 📊\n"
        f"**Risk Level**: {risk}"
    )
    url = f"https://app.bubblemaps.io/{chain}/token/{address}"
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔗 View Bubblemap", url=url)]])

    # send and clean up
    with open(screenshot, "rb") as img:
        await update.message.reply_photo(
            photo=img,
            caption=caption,
            parse_mode="Markdown",
            reply_markup=keyboard,
        )
    os.remove(screenshot)
    increment_scans()
