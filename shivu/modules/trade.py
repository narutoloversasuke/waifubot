from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from shivu import user_collection, shivuu

pending_gifts = {}          
pending_trades = {}         
locked_users = set()        
locked_characters = set()   
cooldowns = {}              
active_buttons = {}        
lock = set()

### ✅ `/trade` Command (Character Exchange)
@shivuu.on_message(filters.command("trade"))
async def trade(client, message):
    sender_id = message.from_user.id

    if not message.reply_to_message:
        await message.reply_text("⚖️ The trade parchment is empty… No waifu matches found! ❌")
        return

    receiver_id = message.reply_to_message.from_user.id

    if sender_id == receiver_id:
        await message.reply_text("You can't trade a character with yourself!")
        return

    if len(message.command) != 3:
        await message.reply_text("You need to provide two character IDs!")
        return

    sender_character_id, receiver_character_id = message.command[1], message.command[2]

    sender = await user_collection.find_one({'id': sender_id})
    receiver = await user_collection.find_one({'id': receiver_id})

    sender_character = next((character for character in sender['characters'] if character['id'] == sender_character_id), None)
    receiver_character = next((character for character in receiver['characters'] if character['id'] == receiver_character_id), None)

    if not sender_character:
        await message.reply_text("⚖️ The trade parchment is empty… No waifu matches found! ❌")
        return

    if not receiver_character:
        await message.reply_text("🌫️ Your offer is met with silence… The trade cannot proceed. ⏳")
        return

    pending_trades[(sender_id, receiver_id)] = (sender_character_id, receiver_character_id)

    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("✅ Confirm Trade", callback_data="confirm_trade")],
            [InlineKeyboardButton("❌ Cancel Trade", callback_data="cancel_trade")]
        ]
    )

    await message.reply_text(f"{message.reply_to_message.from_user.mention}, do you accept this trade?", reply_markup=keyboard)


@shivuu.on_callback_query(filters.create(lambda _, __, query: query.data in ["confirm_trade", "cancel_trade"]))
async def on_trade_callback(client, callback_query):
    receiver_id = callback_query.from_user.id

    for (sender_id, _receiver_id), (sender_character_id, receiver_character_id) in pending_trades.items():
        if _receiver_id == receiver_id:
            break
    else:
        await callback_query.answer("This is not for you!", show_alert=True)
        return

    if callback_query.data == "confirm_trade":
        sender = await user_collection.find_one({'id': sender_id})
        receiver = await user_collection.find_one({'id': receiver_id})

        sender_character = next((character for character in sender['characters'] if character['id'] == sender_character_id), None)
        receiver_character = next((character for character in receiver['characters'] if character['id'] == receiver_character_id), None)

        sender['characters'].remove(sender_character)
        receiver['characters'].remove(receiver_character)

        await user_collection.update_one({'id': sender_id}, {'$set': {'characters': sender['characters']}})
        await user_collection.update_one({'id': receiver_id}, {'$set': {'characters': receiver['characters']}})

        sender['characters'].append(receiver_character)
        receiver['characters'].append(sender_character)

        await user_collection.update_one({'id': sender_id}, {'$set': {'characters': sender['characters']}})
        await user_collection.update_one({'id': receiver_id}, {'$set': {'characters': receiver['characters']}})

        del pending_trades[(sender_id, receiver_id)]

        await callback_query.message.edit_text("🎉 The celestial forces shift in your favor… The divine treasury bestows upon you its riches! ✨")

    elif callback_query.data == "cancel_trade":
        del pending_trades[(sender_id, receiver_id)]
        await callback_query.message.edit_text("🌫️ The cosmic balance rejects this trade… The waifus remain in their original paths. ⏳")


### ✅ `/gift` Command (Character Gifting)
@shivuu.on_message(filters.command("gift"))
async def gift(client, message):
    sender_id = message.from_user.id

    if not message.reply_to_message:
        await message.reply_text("You need to reply to a user's message to gift a character!")
        return

    receiver_id = message.reply_to_message.from_user.id
    receiver_username = message.reply_to_message.from_user.username
    receiver_first_name = message.reply_to_message.from_user.first_name

    if sender_id == receiver_id:
        await message.reply_text("You can't gift a character to yourself!")
        return

    if len(message.command) != 2:
        await message.reply_text("You need to provide a character ID!")
        return

    character_id = message.command[1]

    sender = await user_collection.find_one({'id': sender_id})

    character = next((character for character in sender['characters'] if character['id'] == character_id), None)

    if not character:
        await message.reply_text("The ethereal winds scatter your gift… No such user or waifu exists! 💀")
        return

    pending_gifts[(sender_id, receiver_id)] = {
        'character': character,
        'receiver_username': receiver_username,
        'receiver_first_name': receiver_first_name
    }

    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("✅ Confirm Gift", callback_data="confirm_gift")],
            [InlineKeyboardButton("❌ Cancel Gift", callback_data="cancel_gift")]
        ]
    )

    await message.reply_text(f"Do you really want to gift {message.reply_to_message.from_user.mention}?", reply_markup=keyboard)


@shivuu.on_callback_query(filters.create(lambda _, __, query: query.data in ["confirm_gift", "cancel_gift"]))
async def on_gift_callback(client, callback_query):
    sender_id = callback_query.from_user.id

    for (_sender_id, receiver_id), gift in pending_gifts.items():
        if _sender_id == sender_id:
            break
    else:
        await callback_query.answer("This is not for you!", show_alert=True)
        return

    if callback_query.data == "confirm_gift":
        sender = await user_collection.find_one({'id': sender_id})
        receiver = await user_collection.find_one({'id': receiver_id})

        sender['characters'].remove(gift['character'])
        await user_collection.update_one({'id': sender_id}, {'$set': {'characters': sender['characters']}})

        if receiver:
            await user_collection.update_one({'id': receiver_id}, {'$push': {'characters': gift['character']}})
        else:
            await user_collection.insert_one({
                'id': receiver_id,
                'username': gift['receiver_username'],
                'first_name': gift['receiver_first_name'],
                'characters': [gift['character']],
            })

        del pending_gifts[(sender_id, receiver_id)]

        await callback_query.message.edit_text("🎁 A sacred offering is made… The waifu is now in new hands! ✨")

    elif callback_query.data == "cancel_gift":
        del pending_gifts[(sender_id, receiver_id)]
        await callback_query.message.edit_text("🔥 The blessing is withdrawn… The waifu remains with its owner. 🔮")
