import importlib import time import random import re import asyncio from html import escape

from telegram import InlineKeyboardButton, InlineKeyboardMarkup from telegram import Update from telegram.ext import CommandHandler, CallbackContext, MessageHandler, filters

from shivu import collection, user_collection, application

locks = {} message_counts = {} sent_characters = {} last_characters = {} first_correct_guesses = {} warned_users = {}

for module_name in ALL_MODULES: importlib.import_module("shivu.modules." + module_name)

def escape_markdown(text): escape_chars = r'*_`~>#+-=|{}.!' return re.sub(r'([%s])' % re.escape(escape_chars), r'\1', text)

async def message_counter(update: Update, context: CallbackContext) -> None: chat_id = str(update.effective_chat.id) user_id = update.effective_user.id

if chat_id not in locks:
    locks[chat_id] = asyncio.Lock()

async with locks[chat_id]:
    message_counts[chat_id] = message_counts.get(chat_id, 0) + 1  
    if message_counts[chat_id] % 100 == 0:  
        await send_image(update, context)
        message_counts[chat_id] = 0

async def send_image(update: Update, context: CallbackContext) -> None: chat_id = update.effective_chat.id all_characters = list(await collection.find({}).to_list(length=None))

if chat_id not in sent_characters:
    sent_characters[chat_id] = []

available_characters = [c for c in all_characters if c['id'] not in sent_characters[chat_id]]
if not available_characters:
    sent_characters[chat_id] = []
    available_characters = all_characters

character = random.choice(available_characters)
sent_characters[chat_id].append(character['id'])
last_characters[chat_id] = character

await context.bot.send_photo(
    chat_id=chat_id,
    photo=character['img_url'],
    caption=f"""A New {character['rarity']} Character Appeared...

/grasp Character Name and add in Your Harem""", parse_mode='Markdown' )

async def grasp(update: Update, context: CallbackContext) -> None: chat_id = update.effective_chat.id user_id = update.effective_user.id

if chat_id not in last_characters:
    return

if chat_id in first_correct_guesses:
    await update.message.reply_text('❌ Already Guessed By Someone.. Try Next Time')
    return

guess = ' '.join(context.args).lower() if context.args else ''  
if "()" in guess or "&" in guess:
    await update.message.reply_text("Nahh You Can't use This Types of words in your guess..❌")
    return

character_name = last_characters[chat_id]['name'].lower()
if sorted(character_name.split()) == sorted(guess.split()) or guess in character_name.split():
    first_correct_guesses[chat_id] = user_id

    await user_collection.update_one(
        {'id': user_id},
        {'$set': {
            'username': update.effective_user.username,
            'first_name': update.effective_user.first_name
        }, '$push': {'characters': last_characters[chat_id]}},
        upsert=True
    )

    keyboard = [[InlineKeyboardButton(f"See Harem", switch_inline_query_current_chat=f"collection.{user_id}")]]
    await update.message.reply_text(
        f'📜 "Ancient runes glow as the contract is sealed… {last_characters[chat_id]["name"]} is now bound within your grasp. 🔮"',
        parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard)
    )
else:
    await update.message.reply_text('📜 "The ancient scroll rejects this name… No such waifu exists! ❌"')

async def fav(update: Update, context: CallbackContext) -> None: user_id = update.effective_user.id if not context.args: await update.message.reply_text('Please provide Character ID...') return

character_id = context.args[0]
user = await user_collection.find_one({'id': user_id})
if not user or character_id not in [c['id'] for c in user.get('characters', [])]:
    await update.message.reply_text('This Character is Not In your collection')
    return

await user_collection.update_one({'id': user_id}, {'$set': {'favorites': [character_id]}})
await update.message.reply_text(f'Character has been added to your favorite...')

def main() -> None: application.add_handler(CommandHandler("grasp", grasp, block=False)) application.add_handler(CommandHandler("fav", fav, block=False)) application.add_handler(MessageHandler(filters.ALL, message_counter, block=False)) application.run_polling(drop_pending_updates=True)

if name == "main": main()

