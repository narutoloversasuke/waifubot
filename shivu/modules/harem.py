from telegram import Update
from itertools import groupby
import math
from html import escape
import random
from telegram.ext import CommandHandler, CallbackContext, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from shivu import collection, user_collection, application

rarity_map = {
1: "⚪ Common",
2: "🟣 Rare",
3: "🟢 Medium",
4: "🟡 Legendary",
5: "💮 Special Edition",
6: "🔮 Limited Edition",
7: "🎐 Celestial Beauty",
8: "🕊️ Divine Edition",
9: "💦 Wet Elegance",
10: "🎴 Cosplay"
}

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
total_pages = math.ceil(len(unique_characters) / 8)  # Sirf 8 waifus per page  

page = max(0, min(page, total_pages - 1))  

power_level = len(user['characters'])  
level = (  
    "🔰 Beginner Collector" if power_level <= 10 else  
    "🌟 Rising Enthusiast" if power_level <= 30 else  
    "🔍 Waifu Seeker" if power_level <= 60 else  
    "📜 True Collector" if power_level <= 100 else  
    "🏆 Elite Waifu Hunter" if power_level <= 150 else  
    "🔥 Legendary Keeper" if power_level <= 200 else  
    "🌌 Mythical Waifu Overlord" if power_level <= 400 else  
    "🚀 Cosmic Waifu Emperor" if power_level <= 500 else  
    "💎 Supreme Waifu Deity"  
)  

waifu_message = f"✨ **{escape(update.effective_user.first_name)}'s Waifu Collection** ✨\n"  
waifu_message += f"🏅 **Power Level:** {level}\n"  
waifu_message += f"📖 **Page:** {page + 1}/{total_pages}\n\n"  

current_characters = unique_characters[page*8:(page+1)*8]  
grouped_characters = {k: list(v) for k, v in groupby(current_characters, key=lambda x: x['anime'])}  

for anime, characters in grouped_characters.items():  
    waifu_message += f"🔹 **{anime}** ({len(characters)}/{await collection.count_documents({'anime': anime})})\n"  
    for character in characters:  
        count = character_counts[character['id']]  
        rarity = rarity_map.get(character['rarity'], "❓ Unknown Rarity")  
        waifu_message += f"   ├ {rarity} **{character['name']}** ×{count}\n"  
    waifu_message += "   └───────────────\n"  

total_count = len(user['characters'])  
keyboard = [[InlineKeyboardButton("📜 Waifus", callback_data="open_collection")]]  

if total_pages > 1:  
    nav_buttons = []  
    if page > 0:  
        nav_buttons.append(InlineKeyboardButton("⬅️", callback_data=f"mywaifus:{page-1}:{user_id}"))  
    if page < total_pages - 1:  
        nav_buttons.append(InlineKeyboardButton("➡️", callback_data=f"mywaifus:{page+1}:{user_id}"))  
    keyboard.append(nav_buttons)  

reply_markup = InlineKeyboardMarkup(keyboard)  

if 'favorites' in user and user['favorites']:  
    fav_character_id = user['favorites'][0]  
    fav_character = next((c for c in user['characters'] if c['id'] == fav_character_id), None)  
    if fav_character and 'img_url' in fav_character:  
        if update.message:  
            await update.message.reply_photo(photo=fav_character['img_url'], parse_mode='HTML', caption=waifu_message, reply_markup=reply_markup)  
        else:  
            if update.callback_query.message.caption != waifu_message:  
                await update.callback_query.edit_message_caption(caption=waifu_message, reply_markup=reply_markup, parse_mode='HTML')  
    else:  
        if update.message:  
            await update.message.reply_text(waifu_message, parse_mode='HTML', reply_markup=reply_markup)  
        else:  
            if update.callback_query.message.text != waifu_message:  
                await update.callback_query.edit_message_text(waifu_message, parse_mode='HTML', reply_markup=reply_markup)  
else:  
    if user['characters']:  
        random_character = random.choice(user['characters'])  
        if 'img_url' in random_character:  
            if update.message:  
                await update.message.reply_photo(photo=random_character['img_url'], parse_mode='HTML', caption=waifu_message, reply_markup=reply_markup)  
            else:  
                if update.callback_query.message.caption != waifu_message:  
                    await update.callback_query.edit_message_caption(caption=waifu_message, reply_markup=reply_markup, parse_mode='HTML')  
        else:  
            if update.message:  
                await update.message.reply_text(waifu_message, parse_mode='HTML', reply_markup=reply_markup)  
            else:  
                if update.callback_query.message.text != waifu_message:  
                    await update.callback_query.edit_message_text(waifu_message, parse_mode='HTML', reply_markup=reply_markup)  
    else:  
        if update.message:  
            await update.message.reply_text("🚫 **Your Vault is Empty.** Start collecting waifus now!")

async def mywaifus_callback(update: Update, context: CallbackContext) -> None:
query = update.callback_query
_, page, user_id = query.data.split(':')
page = int(page)
user_id = int(user_id)

if query.from_user.id != user_id:  
    await query.answer("🚫 This isn't your collection!", show_alert=True)  
    return  

await mywaifus(update, context, page)

application.add_handler(CommandHandler(["mywaifus", "collection"], mywaifus, block=False))
application.add_handler(CallbackQueryHandler(mywaifus_callback, pattern='^mywaifus', block=False))

You give me wrong emoji are not matching that's why error occuring

