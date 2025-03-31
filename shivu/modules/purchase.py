from pyrogram import Client, filters
from shivu import db, collection, user_collection
import asyncio
from shivu import shivuu as app
from shivu import sudo_users

DEV_LIST = [7640076990]

async def purchase_character(buyer_id, character_id):
    character = await collection.find_one({'id': character_id})

    if character:
        try:
            await user_collection.update_one(
                {'id': buyer_id},
                {'$push': {'characters': character}}
            )

            img_url = character['img_url']
            caption = (
                f"Purchase Successful for {buyer_id}\n"
                f"Information As Follows\n"
                f" 🎏 𝙍𝙖𝙧𝙞𝙩𝙮: {character['rarity']}\n"
                f"🎐 𝘼𝙣𝙞𝙢𝙚: {character['anime']}\n"
                f"💕 𝙉𝙖𝙢𝙚: {character['name']}\n"
                f"🪅 𝙄𝘿: {character['id']}"
            )

            return img_url, caption
        except Exception as e:
            print(f"Error updating user: {e}")
            raise
    else:
        raise ValueError("Character not found.")

@app.on_message(filters.command(["purchase"]) & filters.reply & filters.user(DEV_LIST))
async def purchase_character_command(_, message):
    if not message.reply_to_message:
        await message.reply_text("You need to reply to a user's message to process a purchase!")
        return

    try:
        character_id = str(message.text.split()[1])
        buyer_id = message.reply_to_message.from_user.id

        result = await purchase_character(buyer_id, character_id)

        if result:
            img_url, caption = result
            await message.reply_photo(photo=img_url, caption=caption)

    except IndexError:
        await message.reply_text("Please provide a character ID.")
    except ValueError as e:
        await message.reply_text(str(e))
    except Exception as e:
        print(f"Error in purchase_character_command: {e}")
        await message.reply_text("An error occurred while processing the purchase.")
