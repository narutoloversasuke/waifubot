from telegram.ext import CommandHandler
from shivu import collection, user_collection, application

async def buy(update, context):
    user_id = update.effective_user.id

    if not context.args or len(context.args) != 1:
        await update.message.reply_text('<b>Please provide a valid pick ID to buy.</b>')
        return

    character_id = context.args[0]
    character = await collection.find_one({'id': character_id})

    if not character:
        await update.message.reply_text('Pick not found in the store.')
        return

    user = await user_collection.find_one({'id': user_id})

    if not user or 'balance' not in user:
        await update.message.reply_text('Error: User balance not found.')
        return

    rarity_coin_mapping = {
        "⚪ Common": 2000000,
        "🟣 Normal": 4000000,
        "🔵 Medium": 8000000,
        "🟡 Legendary": 1500000,
        "💮 Special Edition": 20000000,
        "🔮 Limited Edition": 300000000,
        "🎐 Celestial Beauty": 400000000000
    }

    rarity = character.get('rarity', 'Unknown Rarity')
    coin_cost = rarity_coin_mapping.get(rarity, 0)

    if coin_cost == 0:
        await update.message.reply_text('Invalid rarity. Cannot determine the coin cost.')
        return

    if user['balance'] < coin_cost:
        await update.message.reply_text('Insufficient coins to buy.')
        return

    await user_collection.update_one(
        {'id': user_id},
        {'$push': {'characters': character}, '$inc': {'balance': -coin_cost}}
    )

    character_img_url = character.get('image_url', '')
    character_name = character.get('name', 'Unknown Character')

    purchase_message = (
        f"🎉 **Purchase Successful!** 🎉\n\n"
        f"🆔 **ID:** {character_id}\n"
        f"📛 **Name:** {character_name}\n"
        f"🌟 **Rarity:** {rarity}\n"
        f"💰 **Cost:** {coin_cost} coins"
    )

    if character_img_url:
        await update.message.reply_photo(photo=character_img_url, caption=purchase_message)
    else:
        await update.message.reply_text(purchase_message + "\n⚠️ No image available for this character.")

buy_handler = CommandHandler("buy", buy, block=False)
application.add_handler(buy_handler)
