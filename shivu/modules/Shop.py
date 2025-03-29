from telegram.ext import CommandHandler
from shivu import collection, user_collection, application
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

async def buy(update, context):
    user_id = update.effective_user.id

    # Check if the command includes a character ID  
    if not context.args or len(context.args) != 1:  
        await update.message.reply_text('<b>Please provide a valid pick ID to buy.</b>', parse_mode="HTML")  
        return  

    character_id = context.args[0]  

    # Retrieve the character from the store based on the provided ID  
    character = await collection.find_one({'id': character_id})  
    if not character:  
        await update.message.reply_text('Pick not found in the store.')  
        return  

    # Check if the user has sufficient coins to make the purchase  
    user = await user_collection.find_one({'id': user_id})  
    if not user or 'balance' not in user:  
        await update.message.reply_text('Error: User balance not found.')  
        return  

    # Determine the coin cost based on the rarity of the character  
    rarity_coin_mapping = {  
        "⚪ Common": 2000000,  
        "🟣 Normal": 4000000,  
        "🔵 Medium": 8000000,  
        "🟡 Legendary": 15000000,  
        "💮 Special Edition": 20000000,  
        "🔮 Limited Edition": 300000000,  
        "🎐 Celestial Beauty": 400000000000,   
    }  
          
    rarity = character.get('rarity', 'Unknown Rarity')  
    coin_cost = rarity_coin_mapping.get(rarity, 0)  

    if coin_cost == 0:  
        await update.message.reply_text('Invalid rarity. Cannot determine the coin cost.')  
        return  

    if user['balance'] < coin_cost:  
        await update.message.reply_text('Insufficient coins to buy.')  
        return  

    # Deduct balance and add character to user's collection  
    await user_collection.update_one(  
        {'id': user_id},  
        {'$push': {'characters': character}, '$inc': {'balance': -coin_cost}}  
    )  

    # Get the character's image URL  
    character_img_url = character.get('image_url', None)  

    # Create purchase message  
    purchase_message = (
        f'✅ <b>Purchase Successful!</b>\n'
        f'👤 <b>Character:</b> {character["name"]}\n'
        f'🆔 <b>ID:</b> {character["id"]}\n'
        f'💎 <b>Rarity:</b> {rarity}\n'
        f'💰 <b>Cost:</b> Ŧ{coin_cost:,} 💸'
    )

    # Send image with caption if available, otherwise just text  
    if character_img_url:  
        await update.message.reply_photo(photo=character_img_url, caption=purchase_message, parse_mode="HTML")  
    else:  
        await update.message.reply_text(purchase_message, parse_mode="HTML")  

buy_handler = CommandHandler("buy", buy, block=False)
application.add_handler(buy_handler)
