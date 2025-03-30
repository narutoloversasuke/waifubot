from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from itertools import groupby
import math
import random
from html import escape
from telegram.ext import CommandHandler, CallbackContext, CallbackQueryHandler
from shivu import collection, user_collection, application

# Rarity Mapping
RARITY_MAP = {
    1: "⚪ Common",
    2: "🟣 Rare",
    3: "🟢 Medium",
    4: "🟡 Legendary",
    5: "💮 Special Edition",
    6: "🔮 Limited Edition",
    7: "🎐 Celestial Beauty",
    8: "🪽 Divine Edition",
    9: "💦 Wet Elegance",
    10: "🎴 Cosplay"
}

# User Level Mapping
def get_power_level(power):
    if power <= 10:
        return "🔰 Beginner Collector"
    elif power <= 30:
        return "🌟 Rising Enthusiast"
    elif power <= 60:
        return "🔍 Waifu Seeker"
    elif power <= 100:
        return "📜 True Collector"
    elif power <= 150:
        return "🏆 Elite Waifu Hunter"
    elif power <= 200:
        return "🔥 Legendary Keeper"
    elif power <= 400:
        return "🌌 Mythical Waifu Overlord"
    elif power <= 500:
        return "🚀 Cosmic Waifu Emperor"
    return "💎 Supreme Waifu Deity"

# Waifu Collection Handler
async def mywaifus(update: Update, context: CallbackContext, page=0) -> None:
    user_id = update.effective_user.id
    user = await user_collection.find_one({'id': user_id})

    if not user or 'characters' not in user or not user['characters']:
        msg = '❌ **No Waifus Found!** Start collecting to build your vault.'
        if update.message:
            await update.message.reply_text(msg)
        else:
            await update.callback_query.edit_message_text(msg)
        return

    characters = sorted(user['characters'], key=lambda x: (x['anime'], x['id']))
    character_counts = {k: len(list(v)) for k, v in groupby(characters, key=lambda x: x['id'])}
    unique_characters = list({character['id']: character for character in characters}.values())
    total_pages = math.ceil(len(unique_characters) / 8)  

    page = max(0, min(page, total_pages - 1))
    power_level = get_power_level(len(user['characters']))

    waifu_message = (
        f"✨ **{escape(update.effective_user.first_name)}'s Waifu Collection** ✨\n"
        f"🏅 **Power Level:** {power_level}\n"
        f"📖 **Page:** {page + 1}/{total_pages}\n\n"
    )

    current_characters = unique_characters[page * 8:(page + 1) * 8]
    grouped_characters = {k: list(v) for k, v in groupby(current_characters, key=lambda x: x['anime'])}

    for anime, characters in grouped_characters.items():
        waifu_message += f"🔹 **{anime}** ({len(characters)}/{await collection.count_documents({'anime': anime})})\n"
        for character in characters:
            count = character_counts[character['id']]
            rarity = RARITY_MAP.get(character['rarity'], "❓ Unknown Rarity")
            waifu_message += f"   ├ {rarity} **{character['name']}** ×{count}\n"
        waifu_message += "   └───────────────\n"

    keyboard = [[InlineKeyboardButton("📜 Waifus", callback_data="open_collection")]]
    if total_pages > 1:
        nav_buttons = []
        if page > 0:
            nav_buttons.append(InlineKeyboardButton("⬅️", callback_data=f"mywaifus:{page - 1}:{user_id}"))
        if page < total_pages - 1:
            nav_buttons.append(InlineKeyboardButton("➡️", callback_data=f"mywaifus:{page + 1}:{user_id}"))
        keyboard.append(nav_buttons)

    reply_markup = InlineKeyboardMarkup(keyboard)

    # Favorite Character or Random Image
    fav_character = next((c for c in user['characters'] if 'favorites' in user and user['favorites'] and c['id'] == user['favorites'][0]), None)
    if not fav_character and user['characters']:
        fav_character = random.choice(user['characters'])

    if fav_character and 'img_url' in fav_character:
        if update.message:
            await update.message.reply_photo(photo=fav_character['img_url'], parse_mode='HTML', caption=waifu_message, reply_markup=reply_markup)
        else:
            await update.callback_query.edit_message_caption(caption=waifu_message, reply_markup=reply_markup, parse_mode='HTML')
    else:
        if update.message:
            await update.message.reply_text(waifu_message, parse_mode='HTML', reply_markup=reply_markup)
        else:
            await update.callback_query.edit_message_text(waifu_message, parse_mode='HTML', reply_markup=reply_markup)

# Callback Handler
async def mywaifus_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    _, page, user_id = query.data.split(':')
    page, user_id = int(page), int(user_id)

    if query.from_user.id != user_id:
        await query.answer("🚫 This isn't your collection!", show_alert=True)
        return

    await mywaifus(update, context, page)

# Handlers Registration
application.add_handler(CommandHandler(["mywaifus", "collection"], mywaifus, block=False))
application.add_handler(CallbackQueryHandler(mywaifus_callback, pattern='^mywaifus', block=False))
