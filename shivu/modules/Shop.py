from telegram.ext import CommandHandler, CallbackQueryHandler from telegram import InlineKeyboardMarkup, InlineKeyboardButton from shivu import collection, user_collection, application  # Database connection import random

✅ Rarity-wise price mapping

rarity_prices = { "⚪ Common": 2000000, "🟣 Normal": 4000000, "🔵 Medium": 8000000, "🟡 Legendary": 1500000, "💮 Special Edition": 20000000, "🔮 Limited Edition": 300000000, "🎐 Celestial Beauty": 400000000000 }

✅ Shop Command

async def shop(update, context): characters = await collection.find({"image_url": {"$exists": True, "$ne": ""}}).to_list(length=30)  # Get waifus with images

if not characters:
    await update.message.reply_text("No characters available in the shop right now.")
    return

selected_waifus = random.sample(characters, min(len(characters), 3))  # Select 3 random waifus
message_text = "**🛒 Welcome to the Waifu Shop! 🛒**\n\n"

for char in selected_waifus:
    char_id = char.get("id", "Unknown")
    char_name = char.get("name", "Unnamed Character")
    char_rarity = char.get("rarity", "Unknown Rarity")
    char_price = rarity_prices.get(char_rarity, 0)  # Get price based on rarity
    char_image = char.get("image_url", "")
    
    message_text += f"🆔 **ID:** `{char_id}`\n"
    message_text += f"📛 **Name:** {char_name}\n"
    message_text += f"🌟 **Rarity:** {char_rarity}\n"
    message_text += f"💰 **Price:** {char_price} coins\n"
    message_text += "--------------------------\n"
    
    await update.message.reply_photo(photo=char_image, caption=message_text)
    message_text = ""  # Clear text to avoid duplication

✅ Buy Function

async def buy(update, context): user_id = update.effective_user.id args = context.args

if not args:
    await update.message.reply_text("Usage: /buy <waifu_id>")
    return

character_id = args[0]
character = await collection.find_one({'id': character_id, "image_url": {"$exists": True, "$ne": ""}})
if not character:
    await update.message.reply_text('Character not found in the store.')
    return

user = await user_collection.find_one({'id': user_id})
if not user or 'balance' not in user:
    await update.message.reply_text('Error: User balance not found.')
    return

rarity = character.get('rarity', 'Unknown Rarity')
coin_cost = rarity_prices.get(rarity, 0)

if user['balance'] < coin_cost:
    await update.message.reply_text('❌ Insufficient coins to buy this waifu.')
    return

# ✅ Deduct coins & add character to user inventory
await user_collection.update_one(
    {'id': user_id},
    {'$push': {'characters': character}, '$inc': {'balance': -coin_cost}}
)

character_img_url = character.get('image_url', '')
character_name = character.get('name', 'Unknown Character')

await update.message.reply_photo(
    photo=character_img_url,
    caption=f"🎉 **Purchase Successful!** 🎉\n\n"
            f"🆔 **ID:** {character_id}\n"
            f"📛 **Name:** {character_name}\n"
            f"🌟 **Rarity:** {rarity}\n"
            f"💰 **Cost:** {coin_cost} coins"
)

✅ Add Handlers

shop_handler = CommandHandler("shop", shop, block=False) buy_handler = CommandHandler("buy", buy, block=False)

application.add_handler(shop_handler) application.add_handler(buy_handler)

