import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from core.api_clients import fetch_bubble

async def tokendetails(update: Update, context: ContextTypes.DEFAULT_TYPE):
    token = context.user_data.get('current_token')
    if not token:
        await update.message.reply_text("No token selected. Please input a <chain> <address> first.")
        return

    chain, address = token['chain'], token['address']
    bubble = await fetch_bubble(chain, address)
    if not bubble:
        await update.message.reply_text("Failed to fetch token details.")
        return

    message = (
        "📋 **Token Details** 📋\n\n"
        f"Token: {bubble.get('full_name', 'N/A')} ({bubble.get('symbol', 'N/A')})\n"
        f"Chain: {chain.upper()}\n"
        f"Total Supply: {bubble.get('supply', 'N/A')}\n"
        f"NFT: {'Yes' if bubble.get('is_X721') else 'No'}\n"
        f"Holder Count: {len(bubble.get('nodes', []))}\n"
        f"Transfer Count: {len(bubble.get('links', []))}\n"
    )
    await update.message.reply_text(message, parse_mode="Markdown")

async def top_holders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    token = context.user_data.get('current_token')
    if not token:
        await (update.message.reply_text if update.message else update.callback_query.message.reply_text)(
            "No token selected. Please input a <chain> <address> first."
        )
        return

    chain, address = token['chain'], token['address']
    bubble = await fetch_bubble(chain, address)
    if not bubble or not bubble.get('nodes'):
        await (update.message.reply_text if update.message else update.callback_query.message.reply_text)(
            "No holder data available."
        )
        return

    nodes = bubble['nodes'][:5]  # Top 5 holders
    message = "🏆 **Top Holders** 🏆\n\n" + "\n".join(
        f"{i}. {n['address'][:6]}...{n['address'][-4:]}: {n['percentage']:.2f}%{' (Contract)' if n['is_contract'] else ''}"
        for i, n in enumerate(nodes, 1)
    )
    await (update.message.reply_text if update.message else update.callback_query.message.reply_text)(
        message, parse_mode="Markdown"
    )

async def transfers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        token = context.user_data.get('current_token')
        if not token:
            await update.callback_query.message.reply_text("No token selected. Please input a <chain> <address> first.")
            return

        chain, address = token['chain'], token['address']
        bubble = await fetch_bubble(chain, address)
        if not bubble or not bubble.get('links'):
            await update.callback_query.message.reply_text("No transfer data available.")
            return

        nodes = bubble.get('nodes', [])
        links = sorted(
            bubble['links'],
            key=lambda x: max(float(x.get('forward', 0)), float(x.get('backward', 0))),
            reverse=True
        )[:3]  # Top 3 transfers
        message = "💸 **Recent Transfers** 💸\n\n"
        for i, link in enumerate(links, 1):
            source_idx = link.get('source')
            target_idx = link.get('target')
            if (isinstance(source_idx, int) and isinstance(target_idx, int) and
                    source_idx < len(nodes) and target_idx < len(nodes)):
                source_addr = nodes[source_idx].get('address', 'Unknown')
                target_addr = nodes[target_idx].get('address', 'Unknown')
                amount = max(float(link.get('forward', 0)), float(link.get('backward', 0)))
                message += f"{i}. {source_addr[:6]}... → {target_addr[:6]}...: {amount:.2f} tokens\n"
            else:
                message += f"{i}. Invalid transfer data\n"
        await update.callback_query.message.reply_text(message, parse_mode="Markdown")
    except Exception as e:
        await update.callback_query.message.reply_text("An error occurred while fetching transfers. Please try again.")
        logging.error(f"Error in transfers: {str(e)}", exc_info=True)

async def risk_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    token = context.user_data.get('current_token')
    if not token:
        await update.callback_query.message.reply_text("No token selected. Please input a <chain> <address> first.")
        return

    chain, address = token['chain'], token['address']
    bubble = await fetch_bubble(chain, address)
    if not bubble:
        await update.callback_query.message.reply_text("Failed to fetch risk data.")
        return

    nodes = bubble.get('nodes', [])
    top_10_percent = sum(n['percentage'] for n in nodes[:10]) if nodes else 0
    contract_percent = sum(n['percentage'] for n in nodes if n.get('is_contract')) if nodes else 0
    message = (
        "⚠️ **Risk Analysis** ⚠️\n\n"
        f"Top 10 Holders Ownership: {top_10_percent:.2f}%\n"
        f"Contract Ownership: {contract_percent:.2f}%\n"
        f"Risk Level: {'🔴 High' if top_10_percent > 50 else '🟠 Elevated' if top_10_percent > 30 else '🟢 Low'}"
    )
    await update.callback_query.message.reply_text(message, parse_mode="Markdown")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == 'top_holders':
        await top_holders(update, context)
    elif query.data == 'transfers':
        await transfers(update, context)
    elif query.data == 'risk_analysis':
        await risk_analysis(update, context)
    elif query.data == 'related_tokens':
        await related_tokens(update, context)
    elif query.data == 'cancel':
        context.user_data.pop('current_token', None)
        await query.edit_message_caption("Token context cleared.")

async def related_tokens(update: Update, context: ContextTypes.DEFAULT_TYPE):
    token = context.user_data.get('current_token')
    if not token:
        await (update.message.reply_text if update.message else update.callback_query.message.reply_text)(
            "No token selected. Please input a <chain> <address> first."
        )
        return
    chain, address = token['chain'], token['address']
    bubble = await fetch_bubble(chain, address)
    if not bubble:
        await (update.message.reply_text if update.message else update.callback_query.message.reply_text)(
            "Failed to fetch token data."
        )
        return
    token_links = bubble.get('token_links', [])
    if not token_links:
        await (update.message.reply_text if update.message else update.callback_query.message.reply_text)(
            "No related tokens found."
        )
        return
    message = "🔗 **Related Tokens** 🔗\n\n"
    for link in token_links[:5]:
        related_address = link.get('address')
        related_symbol = link.get('symbol', 'N/A')
        url = f"https://app.bubblemaps.io/{chain}/token/{related_address}"
        message += f"- [{related_symbol}]({url})\n"
    await (update.message.reply_text if update.message else update.callback_query.message.reply_text)(
        message, parse_mode="Markdown"
    )