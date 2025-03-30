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
        await message.reply_text("⚖️ **The celestial trade altar awaits... but finds no offering!** ❌")
        return

    receiver_id = message.reply_to_message.from_user.id

    if sender_id == receiver_id:
        await message.reply_text("🚫 **You cannot trade with your own shadow!**")
        return

    if len(message.command) != 3:
        await message.reply_text("📜 **A trade requires two waifus!** Please provide their IDs.")
        return

    sender_character_id, receiver_character_id = message.command[1], message.command[2]

    sender = await user_collection.find_one({'id': sender_id})
    receiver = await user_collection.find_one({'id': receiver_id})

    sender_character = next((char for char in sender['characters'] if char['id'] == sender_character_id), None)
    receiver_character = next((char for char in receiver['characters'] if char['id'] == receiver_character_id), None)

    if not sender_character:
        await message.reply_text("🔍 **Your waifu roster lacks this warrior... Trade denied!** ❌")
        return

    if not receiver_character:
        await message.reply_text("🌫 **Your counterpart’s offer vanishes into mist... Trade incomplete.** ⏳")
        return

    pending_trades[(sender_id, receiver_id)] = (sender_character_id, receiver_character_id)

    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("✅ Accept Trade", callback_data="confirm_trade")],
            [InlineKeyboardButton("❌ Reject Trade", callback_data="cancel_trade")]
        ]
    )

    await message.reply_text(f"🔄 **{message.reply_to_message.from_user.mention}, a grand trade is proposed! Do you accept?**", reply_markup=keyboard)


@shivuu.on_callback_query(filters.create(lambda _, __, query: query.data in ["confirm_trade", "cancel_trade"]))
async def on_trade_callback(client, callback_query):
    receiver_id = callback_query.from_user.id

    for (sender_id, _receiver_id), (sender_character_id, receiver_character_id) in pending_trades.items():
        if _receiver_id == receiver_id:
            break
    else:
        await callback_query.answer("🚫 **This is not your trade to decide!**", show_alert=True)
        return

    if callback_query.data == "confirm_trade":
        sender = await user_collection.find_one({'id': sender_id})
        receiver = await user_collection.find_one({'id': receiver_id})

        sender_character = next((char for char in sender['characters'] if char['id'] == sender_character_id), None)
        receiver_character = next((char for char in receiver['characters'] if char['id'] == receiver_character_id), None)

        sender['characters'].remove(sender_character)
        receiver['characters'].remove(receiver_character)

        await user_collection.update_one({'id': sender_id}, {'$set': {'characters': sender['characters']}})
        await user_collection.update_one({'id': receiver_id}, {'$set': {'characters': receiver['characters']}})

        sender['characters'].append(receiver_character)
        receiver['characters'].append(sender_character)

        await user_collection.update_one({'id': sender_id}, {'$set': {'characters': sender['characters']}})
        await user_collection.update_one({'id': receiver_id}, {'$set': {'characters': receiver['characters']}})

        del pending_trades[(sender_id, receiver_id)]

        await callback_query.message.edit_text("🎉 **The heavens rejoice! The waifu exchange is complete!** ✨")

    elif callback_query.data == "cancel_trade":
        del pending_trades[(sender_id, receiver_id)]
        await callback_query.message.edit_text("💔 **The trade was cast into oblivion... The waifus remain unchanged.**")


### ✅ `/gift` Command (Character Gifting)
@shivuu.on_message(filters.command("gift"))
async def gift(client, message):
    sender_id = message.from_user.id

    if not message.reply_to_message:
        await message.reply_text("🎁 **A gift must have a recipient! Reply to someone’s message.**")
        return

    receiver_id = message.reply_to_message.from_user.id
    receiver_username = message.reply_to_message.from_user.username
    receiver_first_name = message.reply_to_message.from_user.first_name

    if sender_id == receiver_id:
        await message.reply_text("🚫 **One cannot gift a waifu to oneself!**")
        return

    if len(message.command) != 2:
        await message.reply_text("📜 **Provide the waifu’s ID for the offering!**")
        return

    character_id = message.command[1]

    sender = await user_collection.find_one({'id': sender_id})

    character = next((char for char in sender['characters'] if char['id'] == character_id), None)

    if not character:
        await message.reply_text("💀 **The void swallows your offering… No such waifu exists!**")
        return

    pending_gifts[(sender_id, receiver_id)] = {
        'character': character,
        'receiver_username': receiver_username,
        'receiver_first_name': receiver_first_name
    }

    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("✅ Bestow Gift", callback_data="confirm_gift")],
            [InlineKeyboardButton("❌ Revoke Gift", callback_data="cancel_gift")]
        ]
    )

    await message.reply_text(f"🎁 **Do you truly wish to gift {message.reply_to_message.from_user.mention} this waifu?**", reply_markup=keyboard)


@shivuu.on_callback_query(filters.create(lambda _, __, query: query.data in ["confirm_gift", "cancel_gift"]))
async def on_gift_callback(client, callback_query):
    sender_id = callback_query.from_user.id

    for (_sender_id, receiver_id), gift in pending_gifts.items():
        if _sender_id == sender_id:
            break
    else:
        await callback_query.answer("🚫 **This is not your gift to decide!**", show_alert=True)
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

        await callback_query.message.edit_text("🎁 **A sacred offering is made… The waifu now belongs to another!** ✨")

    elif callback_query.data == "cancel_gift":
        del pending_gifts[(sender_id, receiver_id)]
        await callback_query.message.edit_text("🔥 **The cosmic decree has been reversed… The waifu remains where it was.**")
