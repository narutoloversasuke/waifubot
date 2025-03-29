from telegram.ext import CommandHandler, CallbackQueryHandler
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from shivu import collection, user_collection, application  # Database connection

# ✅ Rarity-wise price mapping
rarity_prices = {
    "⚪ Common": 2000000,
    "🟣 Normal": 4000000,
    "🔵 Medium": 8000000,
    "🟡 Legendary": 1500000,
    "💮 Special Edition": 20000000,
    "🔮 Limited Edition": 300000000,
    "🎐 Celestial Beauty": 400000000000
}

# ✅ Shop Command
async def shop(update, context):
    characters = await collection.find().to_list(length=10)  # Fetch 10 waifus from database

    if not characters:
        await update.message.reply_text("No characters available in the shop right now.")
        return

    message_text = "**🛒 Welcome to the Waifu Shop! 🛒**\n\n"
    buttons = []

    for char in characters:
        char_id = char.get("id", "Unknown")
        char_name = char.get("name", "Unnamed Character")
        char_rarity = char.get("rarity", "Unknown Rarity")
        char_price = rarity_prices.get(char_rarity, 0)  # Get price based on rarity

        message_text += f"🆔 **ID:** `{char_id}`\n"
        message_text += f"📛 **Name:** {char_name}\n"
        message_text += f"🌟 **Rarity:** {char_rarity}\n"
        message_text += f"💰 **Price:** {char_price} coins\n"
        message_text += "--------------------------\n"

        buttons.append([InlineKeyboardButton(f"Buy {char_name}", callback_data=f"buy_{char_id}")])

    reply_markup = InlineKeyboardMarkup(buttons)
    await update.message.reply_text(message_text, reply_markup=reply_markup)

# ✅ Buy Command
async def buy(update, context):
    user_id = update.effective_user.id

    if not context.args or len(context.args) != 1:
        await update.message.reply_text('<b>Please provide a valid pick ID to buy.</b>')
        return

    character_id = context.args[0]  # Get ID from command

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
    if character_img_url:
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

# ✅ Handle Button Clicks
async def handle_button_click(update, context):
    query = update.callback_query
    data = query.data

    if data.startswith("buy_"):
        character_id = data.split("_")[1]  # Extract character ID
        context.args = [character_id]  # Pass ID to buy function
        await buy(update, context)  # Call buy function

# ✅ Add Handlers
shop_handler = CommandHandler("shop", shop, block=False)
buy_handler = CommandHandler("buy", buy, block=False)
callback_handler = CallbackQueryHandler(handle_button_click)

application.add_handler(shop_handler)
application.add_handler(buy_handler)
application.add_handler(callback_handler)
