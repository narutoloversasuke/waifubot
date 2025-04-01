from telegram.ext import CommandHandler
from shivu import collection, user_collection, application
from telegram import InputMediaPhoto

# 🛒 SHOP SYSTEM (Now with Image!)
async def shop(update, context):
    shop_message = (
        "🌸 **Welcome to the Waifu Shop!** 🌸\n\n"
        "🔹 **Available Waifus:**\n"
        "⚪ Common: Ŧ2,00,000 💸\n"
        "🟣 Normal: Ŧ3,00,000 💸\n"
        "🔵 Medium: Ŧ4,00,000 💸\n"
        "🟡 Legendary: Ŧ5,00,000 💸\n"
        "💮 Special Edition: Ŧ8,00,000 💸\n"
        "🔮 Limited Edition: Ŧ9,00,000 💸\n"
        "🎐 Celestial Beauty: Ŧ11,00,000 💸\n\n"
        "✨ **Only the worthy can claim the rarest waifus!** ✨\n"
        "👉 **To Buy a Waifu, use:** `/buy <pick_id>`"
    )

    shop_image = "https://postimg.cc/GBkNSQVq"  # Shop Banner Image

    await update.message.reply_photo(photo=shop_image, caption=shop_message, parse_mode="Markdown")

shop_handler = CommandHandler("shop", shop, block=False)
application.add_handler(shop_handler)

# 💸 BUY SYSTEM (Now With Image!)
async def buy(update, context):
    user_id = update.effective_user.id

    if not context.args or len(context.args) != 1:
        await update.message.reply_text('<b>Please provide a valid pick ID to buy.</b>', parse_mode="HTML")
        return

    character_id = context.args[0]
    character = await collection.find_one({'id': character_id})

    if not character:
        await update.message.reply_text('<b>Pick not found in the store.</b>', parse_mode="HTML")
        return

    user = await user_collection.find_one({'id': user_id})

    if not user or 'balance' not in user:
        await update.message.reply_text('<b>Error: User balance not found.</b>', parse_mode="HTML")
        return

    # 📌 Price Mapping
    rarity_prices = {
        "⚪ Common": 200000,
        "🟣 Normal": 300000,
        "🔵 Medium": 400000,
        "🟡 Legendary": 500000,
        "💮 Special Edition": 800000,
        "🔮 Limited Edition": 9000000,
        "🎐 Celestial Beauty": 1100000,
    }

    rarity = character.get('rarity', 'Unknown Rarity')
    price = rarity_prices.get(rarity, 0)

    if price == 0:
        await update.message.reply_text('<b>Invalid rarity. Cannot determine the price.</b>', parse_mode="HTML")
        return

    if user['balance'] < price:
        await update.message.reply_text('<b>Insufficient coins to buy.</b>', parse_mode="HTML")
        return

    # ✅ Purchase Successful
    await user_collection.update_one(
        {'id': user_id},
        {'$push': {'characters': character}, '$inc': {'balance': -price}}
    )

    # 🖼 Character Image
    character_image = character.get('image_url', None)  # Check if image exists
    success_message = f'🎉 **Success!** You have purchased **{character["name"]}** for Ŧ{price} 💸'

    if character_image:
        await update.message.reply_photo(photo=character_image, caption=success_message, parse_mode="Markdown")
    else:
        await update.message.reply_text(success_message, parse_mode="Markdown")

buy_handler = CommandHandler("buy", buy, block=False)
application.add_handler(buy_handler)
