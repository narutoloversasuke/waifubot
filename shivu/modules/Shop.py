from telegram.ext import CommandHandler
from shivu import collection, user_collection, application
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

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
        "🎐 Celestial Beauty": 400000000000,
    }

    rarity = character.get('rarity', 'Unknown Rarity')
    coin_cost = rarity_coin_mapping.get(rarity, 0)

    if coin_cost == 0:
        await update.message.reply_text('Invalid rarity. Cannot determine the coin cost.')
        return

    if user['balance'] < coin_cost:
        await update.message.reply_text('Insufficient coins to buy')
        return

    await user_collection.update_one(
        {'id': user_id},
        {'$push': {'characters': character}, '$inc': {'balance': -coin_cost}}
    )

    image_url = character.get('image_url', '')

    await update.message.reply_photo(
        photo=image_url,
        caption=f'Success! You have purchased {character["name"]} for {coin_cost} coins.'
    )

buy_handler = CommandHandler("buy", buy, block=False)
application.add_handler(buy_handler)

async def shop(update, context):
    message_text = (
        "🛍️ **Waifu Shop** 🛍️\n"
        "\n⚪ Common: Ŧ2,000,000 💸"
        "\n🟣 Normal: Ŧ4,000,000 💸"
        "\n🔵 Medium : Ŧ8,000,000 💸"
        "\n🟡 Legendary: Ŧ15,000,000 💸"
        "\n💮 Special Edition: Ŧ20,000,000 💸"
        "\n🔮 Limited Edition: Ŧ300,000,000 💸"
        "\n🎐 Celestial Beauty: Ŧ4,000,000,000 💸"
        "\n\n💳 Use: `/buy <pick_id>`"
    )
    await update.message.reply_text(message_text)

shop_handler = CommandHandler("store", shop, block=False)
application.add_handler(shop_handler)

from pyrogram import Client, filters
from shivu import shivuu as app, sudo_users

DEV_LIST = [7640076990]

async def purchase_character(buyer_id, character_id):
    character = await collection.find_one({'id': character_id})

    if character:
        try:
            buyer = await user_collection.find_one({'id': buyer_id})
            if not buyer:
                raise ValueError("User not found.")
            
            await user_collection.update_one(
                {'id': buyer_id},
                {'$push': {'characters': character}}
            )
            
            image_url = character['image_url']
            caption = (
                f"Successfully Purchased By {buyer['name']} ({buyer_id})\n"
                f"🎏 𝙍𝙖𝙧𝙞𝙩𝙮: {character['rarity']}\n"
                f"🎐 𝘼𝙣𝙞𝙢𝙚: {character['anime']}\n"
                f"💕 𝙉𝙖𝙢𝙚: {character['name']}\n"
                f"🪅 𝙄𝘿: {character['id']}"
            )
            return image_url, caption
        except Exception as e:
            print(f"Error updating user: {e}")
            raise
    else:
        raise ValueError("Character not found.")

@app.on_message(filters.command(["buy"]) & filters.user(DEV_LIST))
async def buy_character_command(_, message):
    try:
        character_id = str(message.text.split()[1])
        buyer_id = message.from_user.id

        result = await purchase_character(buyer_id, character_id)
        
        if result:
            image_url, caption = result
            await message.reply_photo(photo=image_url, caption=caption)
    
    except IndexError:
        await message.reply_text("Please provide a character ID.")
    except ValueError as e:
        await message.reply_text(str(e))
    except Exception as e:
        print(f"Error in buy_character_command: {e}")
        await message.reply_text("An error occurred while processing the purchase.")
