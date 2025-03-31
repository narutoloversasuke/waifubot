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
SUPPORT_CHAT_ID = -1002236898779  # Group Chat ID
CHARACTER_CHANNEL_ID = -1002236898779  # Change this to the correct character channel ID

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
    "⚪ Common": 50,  # 50% chance
    "🟣 Rare": 25,  # 25% chance
    "🟢 Medium": 12,  # 12% chance
    "🟡 Legendary": 6,  # 6% chance
    "💮 Special Edition": 4,  # 4% chance
    "🔮 Limited Edition": 2,  # 2% chance
    "🎐 Celestial Beauty": 1,  # 1% chance
}

async def get_claim_state():
    """Fetch the claim state from the database"""
    doc = await collection.find_one({})
    return doc.get("claim", "False")

async def get_random_rarity():
    """Get a random rarity based on weighted chances"""
    total = sum(rarity_chances.values())
    rand = random.randint(1, total)
    cumulative = 0
    for rarity, chance in rarity_chances.items():
        cumulative += chance
        if rand <= cumulative:
            return rarity
    return "⚪ Common"

async def get_random_character(rarity):
    """Fetch a random character from the database based on rarity"""
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
    mention = message.from_user.mention

    # Check if the user is in the required group chat
    try:
        member = await bot.get_chat_member(SUPPORT_CHAT_ID, user_id)
    except UserNotParticipant:
        return await message.reply_text("You need to join the chat to use this feature.", reply_markup=keyboard)

    # Ensure the command is used in the correct group chat
    if chat_id != SUPPORT_CHAT_ID:
        return await message.reply_text("Command can only be used here: 𝖮𝗍𝖺𝗄𝗎 𝖲𝗊𝗎𝖺𝖽𝖾 𝖠𝗅𝗅𝗂𝖺𝗇𝖼𝖾")

    # Check if the claim feature is enabled
    claim_state = await get_claim_state()
    if claim_state == "False":
        return await message.reply_text("Claiming feature is currently disabled.")

    # Prevent multiple claims per day
    now = datetime.now()
    if user_id in last_claim_time and last_claim_time[user_id].date() == now.date():
        return await message.reply_text(f"𝖸𝗈𝗎'𝗏𝖾 𝖺𝗅𝗋𝖾𝖺𝖽𝗒 𝖼𝗅𝖺𝗂𝗆𝖾𝖽 𝗍𝗈𝖽𝖺𝗒. 𝖢𝗈𝗆𝖾 𝖻𝖺𝖼𝗄 𝗍𝗈𝗆𝗈𝗋𝗋𝗈𝗐!")

    # Generate random character
    rarity = await get_random_rarity()
    character = await get_random_character(rarity)

    if character:
        # Store character in user collection
        await user_collection.update_one({'id': user_id}, {'$push': {'characters': character}}, upsert=True)

        # Send claim message to group chat
        await message.reply_photo(
            photo=character['img_url'],
            caption=f"<b>🎉 Congratulations {mention}!</b>\n\n"
                    f"<b>🎀 Name:</b> {character['name']}\n"
                    f"<b>⚜️ Anime:</b> {character['anime']}\n"
                    f"<b>🌟 Rarity:</b> {rarity}\n\n"
                    "Come back tomorrow for your next claim! 🍀",
            parse_mode='HTML'
        )

        # Send notification to character channel
        await bot.send_message(
            CHARACTER_CHANNEL_ID,
            f"🔔 **New Waifu Claimed!**\n\n"
            f"👤 **User:** {mention}\n"
            f"🎀 **Name:** {character['name']}\n"
            f"⚜️ **Anime:** {character['anime']}\n"
            f"🌟 **Rarity:** {rarity}",
            disable_web_page_preview=True
        )
    else:
        await message.reply_text("No characters found for claiming.")
