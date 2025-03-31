import importlib
import time
import random
import re
import asyncio
from html import escape 

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext, MessageHandler, filters

from shivu import collection, top_global_groups_collection, group_user_totals_collection, user_collection, user_totals_collection, shivuu
from shivu import application, SUPPORT_CHAT, UPDATE_CHAT, db, LOGGER
from shivu.modules import ALL_MODULES

import os

import time
from pyrogram import Client

locks = {}
message_counters = {}
spam_counters = {}
last_characters = {}
sent_characters = {}
first_correct_guesses = {}
message_counts = {}

for module_name in ALL_MODULES:
    imported_module = importlib.import_module("shivu.modules." + module_name)

last_user = {}
warned_users = {}

def escape_markdown(text):
    escape_chars = r'\\*_`\\~>#+-=|{}.!'
    return re.sub(r'([%s])' % re.escape(escape_chars), r'\\\1', text)

async def message_counter(update: Update, context: CallbackContext) -> None:
    chat_id = str(update.effective_chat.id)
    user_id = update.effective_user.id

    if chat_id not in locks:
        locks[chat_id] = asyncio.Lock()
    lock = locks[chat_id]

    async with lock:
        chat_frequency = await user_totals_collection.find_one({'chat_id': chat_id})
        message_frequency = chat_frequency.get('message_frequency', 100) if chat_frequency else 100

        if chat_id in last_user and last_user[chat_id]['user_id'] == user_id:
            last_user[chat_id]['count'] += 1
            if last_user[chat_id]['count'] >= 10:
                if user_id in warned_users and time.time() - warned_users[user_id] < 600:
                    return
                else:
                    await update.message.reply_text("⏳ Whoa! Slow down there! 🛑\nYou need to wait 10 minutes before grasping again!")
                    warned_users[user_id] = time.time()
                    return
        else:
            last_user[chat_id] = {'user_id': user_id, 'count': 1}

        if chat_id in message_counts:
            message_counts[chat_id] += 1
        else:
            message_counts[chat_id] = 1

        if message_counts[chat_id] % message_frequency == 0:
            await send_image(update, context)
            message_counts[chat_id] = 0
            
async def send_image(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id
    all_characters = list(await collection.find({}).to_list(length=1000))
    
    if chat_id not in sent_characters:
        sent_characters[chat_id] = []
    
    if len(sent_characters[chat_id]) == len(all_characters):
        sent_characters[chat_id] = []

    character = random.choice([c for c in all_characters if c['id'] not in sent_characters[chat_id]])
    sent_characters[chat_id].append(character['id'])
    last_characters[chat_id] = character
    
    if chat_id in first_correct_guesses:
        del first_correct_guesses[chat_id]

    await context.bot.send_photo(
        chat_id=chat_id,
        photo=character['img_url'],
        caption=f"💫 A wild waifu has appeared! 💖 {character['name']} ({character['rarity']}) is waiting!\n⚡ Type /grasp [Character Name] before someone else steals her!",
        parse_mode='Markdown')

async def grasp(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    if chat_id not in last_characters:
        await update.message.reply_text("🚀 Whoosh! The waifu vanished into the waifu realm! 🌟 Be quicker next time!")
        return

    if chat_id in first_correct_guesses:
        await update.message.reply_text("⏳ Oops! Too slow! This waifu has already been taken! 💔")
        return

    guess = ' '.join(context.args).lower() if context.args else ''
    
    if not guess:
        await update.message.reply_text("🤔 Huh? Who are you trying to grasp?\n📌 Use /grasp [Character Name] to claim!")
        return
    
    if "()" in guess or "&" in guess.lower():
        await update.message.reply_text("❌ That waifu doesn’t exist in the system! 🔍 Double-check and try again!")
        return

    name_parts = last_characters[chat_id]['name'].lower().split()
    
    if sorted(name_parts) == sorted(guess.split()) or any(part == guess for part in name_parts):
        first_correct_guesses[chat_id] = user_id

        await user_collection.update_one({'id': user_id}, {'$push': {'characters': last_characters[chat_id]}}, upsert=True)
        
        keyboard = [[InlineKeyboardButton(f"See Harem", switch_inline_query_current_chat=f"collection.{user_id}")]]
        await update.message.reply_text(
            f"🎉 Congratulations! {last_characters[chat_id]['name']} is now yours! 💞\n📖 Check your collection to see her!",
            parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.message.reply_text("😵 Oops! That’s the wrong name! ⏳ Try again before it’s too late!")

async def fav(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    
    if not context.args:
        await update.message.reply_text("Please provide Character id...")
        return

    character_id = context.args[0]
    user = await user_collection.find_one({'id': user_id})
    
    if not user or 'characters' not in user:
        await update.message.reply_text("📭 Your waifu list is empty… 💔\n💡 Use /grasp to start collecting your waifus!")
        return

    character = next((c for c in user['characters'] if c['id'] == character_id), None)
    
    if not character:
        await update.message.reply_text("🚫 Hey! You can’t favorite someone else’s waifu! 😡\n🏆 Claim her first with /grasp!")
        return

    await user_collection.update_one({'id': user_id}, {'$set': {'favorites': [character_id]}})
    await update.message.reply_text(f"💖 {character['name']} is now your Favorite Waifu! 🌸⭐ Check your favorites anytime!")

def main() -> None:
    application.add_handler(CommandHandler(["grasp"], grasp))
    application.add_handler(CommandHandler("fav", fav))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_counter))
    application.run_polling(drop_pending_updates=True)
    
if __name__ == "__main__":
    shivuu.start()
    LOGGER.info("Bot started")
    main()
