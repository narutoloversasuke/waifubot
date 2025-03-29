from telegram.ext import CommandHandler, CallbackContext
from telegram import Update
from shivu import collection, user_collection, application  # Database connection

# ✅ Rarity-wise price mapping
rarity_prices = {
    "⚪ Common": 2000000,
    "🟣 Normal": 4000000,
    "🔵 Medium": 8000000,
    "🟡 Legendary": 15000000,
    "💮 Special Edition": 20000000,
    "🔮 Limited Edition": 300000000,
    "🎐 Celestial Beauty": 400000000000
}

# ✅ Shop Command (Shows Waifus With Images)
async def shop(update: Update, context: CallbackContext):
    characters = await collection.find().to_list(length=10)  # Fetch 10 waifus from database

    if not characters:
        await update.message.reply_text("No characters available in the shop right now.")
        return

    await update.message.reply_text("🛒 **Welcome to the Waifu Shop!** 🛒\n\nHere are the available waifus:")

    for char in characters:
        char_id = char.get("id", "Unknown")
        char_name = char.get("name", "Unnamed Character")
        char_rarity = char.get("rarity", "Unknown Rarity")
        char_price = rarity_prices.get(char_rarity, 0)  # Get price based on rarity
        char_image = char.get("image_url", None)  # ✅ Fetch image URL from database

        caption = (
            f"🆔 **ID:** `{char_id}`\n"
            f"📛 **Name:** {char_name}\n"
            f"🌟 **Rarity:** {char_rarity}\n"
            f"💰 **Price:** {char_price} coins\n"
            f"To buy, use: `/buy {char_id}`"
        )

        if char_image and char_image.startswith("http"):
            await update.message.reply_photo(photo=char_image, caption=caption)  # ✅ Send image with details
        else:
            await update.message.reply_text(caption + "\n⚠️ *No image available.*")  # ✅ Send text with warning

# ✅ Buy Function (Handles Purchase)
async def buy(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    args = context.args

    if not args:
        await update.message.reply_text("Usage: `/buy <waifu_id>`")
        return

    character_id = args[0]

    # ✅ Fetch character details from store
    character = await collection.find_one({'id': character_id})
    if not character:
        await update.message.reply_text('Character not found in the store.')
        return

    # ✅ Fetch user details
    user = await user_collection.find_one({'id': user_id})
    if not user or 'balance' not in user:
        await update.message.reply_text('Error: User balance not found.')
        return

    # ✅ Check price & user's balance
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

    # ✅ Fetch character image
    character_img_url = character.get('image_url', '')
    character_name = character.get('name', 'Unknown Character')

    # ✅ Send purchase success message with image
    if character_img_url and character_img_url.startswith("http"):
        await update.message.reply_photo(
            photo=character_img_url,
            caption=f"🎉 **Purchase Successful!** 🎉\n\n"
                    f"🆔 **ID:** {character_id}\n"
                    f"📛 **Name:** {character_name}\n"
                    f"🌟 **Rarity:** {rarity}\n"
                    f"💰 **Cost:** {coin_cost} coins"
        )
    else:
        await update.message.reply_text(
            f"🎉 **Purchase Successful!** 🎉\n\n"
            f"🆔 **ID:** {character_id}\n"
            f"📛 **Name:** {character_name}\n"
            f"🌟 **Rarity:** {rarity}\n"
            f"💰 **Cost:** {coin_cost} coins\n"
            f"⚠️ No image available for this character."
        )

# ✅ Add Handlers
shop_handler = CommandHandler("shop", shop, block=False)
buy_handler = CommandHandler("buy", buy, block=False)

application.add_handler(shop_handler)
application.add_handler(buy_handler)
