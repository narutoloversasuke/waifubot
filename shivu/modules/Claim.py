import asyncio
import html
import random
from pyrogram import filters, Client, types as t
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from shivu import shivuu as bot
from shivu import user_collection, collection
from datetime import datetime, timedelta
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant

DEVS = (6087651372)  # Developer user IDs
SUPPORT_CHAT_ID = -1002236898779  # Updated Group Chat ID

keyboard = InlineKeyboardMarkup([
    [InlineKeyboardButton("Join Chat To Use Me", url="https://t.me/+ZTeO__YsQoIwNTVl")],
    [InlineKeyboardButton("Join Chat To Use Me", url="https://t.me/Anime_P_F_P")]
])

rarity_map = {
    1: "⚪ Common",
    2: "🟣 Rare",
    3: "🟢 Medium",
    4: "🟡 Legendary",
    5: "💮 Special Edition",
    6: "🔮 Limited Edition",
    7: "🎐 Celestial Beauty",
}

rarity_chances = {
    "⚪ Common": 5,  # 50% chance
    "🟣 Rare": 20,  # 25% chance
    "🟢 Medium": 30,  # 12% chance
    "🟡 Legendary": 20,  # 6% chance
    "💮 Special Edition": 16,  # 4% chance
    "🔮 Limited Edition": 10,  # 2% chance
    "🎐 Celestial Beauty": 9,  # 1% chance
}

async def claim_toggle(claim_state):
    await collection.update_one({}, {"$set": {"claim": claim_state}}, upsert=True)

async def get_claim_state():
    doc = await collection.find_one({})
    return doc.get("claim", "False")

async def get_random_rarity():
    total = sum(rarity_chances.values())
    rand = random.randint(1, total)
    cumulative = 0
    for rarity, chance in rarity_chances.items():
        cumulative += chance
        if rand <= cumulative:
            return rarity
    return "⚪ Common"

async def get_random_character(rarity):
    try:
        pipeline = [
            {'$match': {'rarity': rarity}},
            {'$sample': {'size': 1}}
        ]
        cursor = collection.aggregate(pipeline)
        characters = await cursor.to_list(length=1)
        return characters[0] if characters else None
    except Exception as e:
        print(f"Error in get_random_character: {e}")
        return None

last_claim_time = {}

@bot.on_message(filters.command(["claim"]))
async def claim(_, message: t.Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    try:
        member = await bot.get_chat_member(SUPPORT_CHAT_ID, user_id)
        if not member:
            await message.reply_text("You need to join the chat to use this feature.", reply_markup=keyboard)
            return 

        if chat_id != SUPPORT_CHAT_ID:
            return await message.reply_text("Command can only be used here: 𝖮𝗍𝖺𝗄𝗎 𝖲𝗊𝗎𝖺𝖽𝖾 𝖠𝗅𝗅𝗂𝖺𝗇𝖼𝖾 ")

        mention = message.from_user.mention

        claim_state = await get_claim_state(True)
        if claim_state == "False":
            return await message.reply_text("Claiming feature is currently disabled.")

        now = datetime.now()
        if user_id in last_claim_time and last_claim_time[user_id].date() == now.date():
            return await message.reply_text(f"𝖸𝗈𝗎'𝗏𝖾 𝖺𝗅𝗋𝖾𝖺𝖽𝗒 𝖼𝗅𝖺𝗂𝗆𝖾𝖽 𝗍𝗈𝖽𝖺𝗒. 𝖢𝗈𝗆𝖾 𝖻𝖺𝖼𝗄 𝗍𝗈𝗆𝗈𝗋𝗋𝗈𝗐!")

        last_claim_time[user_id] = now
        rarity = await get_random_rarity()
        character = await get_random_character(rarity)

        if character:
            await user_collection.update_one({'id': user_id}, {'$push': {'characters': character}})
            await message.reply_photo(
                photo=character['img_url'],
                caption=f"<b>🎉 Congratulations {mention}!</b>\n\n"
                        f"<b>🎀 Name:</b> {character['name']}\n"
                        f"<b>⚜️ Anime:</b> {character['anime']}\n"
                        f"<b>🌟 Rarity:</b> {rarity}\n\n"
                        "Come back tomorrow for your next claim! 🍀",
                parse_mode='HTML'
            )
        else:
            await message.reply_text("No characters found for claiming.")
    except Exception as e:
        print(f"An error occurred in claim: {e}")
