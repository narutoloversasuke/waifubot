from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler
from shivu import collection, user_collection, application

# ✅ Rarity Mapping with Fixed Prices
RARITY_PRICES = {
    "⚪ Common": 2000000,
    "🟣 Normal": 4000000,
    "🔵 Medium": 8000000,
    "🟡 Legendary": 1500000,
    "💮 Special Edition": 20000000,
    "🔮 Limited Edition": 300000000,
    "🎐 Celestial Beauty": 400000000000, 
}

# ✅ Step 1: User Sends /buy, Bot Shows Buttons
async def buy(update, context):
    user_id = update.effective_user.id

    # Check if character ID is provided
    if not context.args or len(context.args) != 1:
        await update.message.reply_text('<b>Please provide a valid pick ID to buy.</b>')
        return

    character_id = context.args[0]

    # Retrieve character details
    character = await collection.find_one({'id': character_id})
    if not character:
        await update.message.reply_text('Pick not found in the store.')
        return

    # Show rarity selection buttons
    keyboard = [
        [InlineKeyboardButton(rarity, callback_data=f"buy_{character_id}_{rarity}")] 
        for rarity in RARITY_PRICES.keys()
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Select the rarity for purchase:", reply_markup=reply_markup)

# ✅ Step 2: Handle Button Clicks
async def buy_callback(update, context):
    query = update.callback_query
    data_parts = query.data.split("_")
    
    if len(data_parts) < 3:
        await query.answer("Invalid selection!")
        return
    
    user_id = query.from_user.id
    character_id = data_parts[1]
    rarity = "_".join(data_parts[2:])  # In case rarity has spaces

    # Check if rarity is valid
    if rarity not in RARITY_PRICES:
        await query.answer("Invalid rarity selection!")
        return
    
    coin_cost = RARITY_PRICES[rarity]

    # Fetch user balance
    user = await user_collection.find_one({'id': user_id})
    if not user or 'balance' not in user:
        await query.answer("Error: User balance not found.")
        return

    if user['balance'] < coin_cost:
        await query.answer("Insufficient coins to buy.")
        return
    
    # Fetch the selected character
    character = await collection.find_one({'id': character_id})
    if not character:
        await query.answer("Character not found.")
        return

    # Deduct balance and add character to user's collection
    await user_collection.update_one(
        {'id': user_id},
        {'$push': {'characters': character}, '$inc': {'balance': -coin_cost}}
    )

    # Send confirmation message
    character_img_url = character.get('image_url', '')
    msg = f'✅ You have purchased {character["name"]} ({rarity}) for {coin_cost} coins!'
    
    if character_img_url:
        await query.message.reply_photo(photo=character_img_url, caption=msg)
    else:
        await query.message.reply_text(msg)

    await query.answer()

# ✅ Register Handlers
buy_handler = CommandHandler("buy", buy, block=False)
buy_callback_handler = CallbackQueryHandler(buy_callback, pattern="^buy_")

application.add_handler(buy_handler)
application.add_handler(buy_callback_handler)
