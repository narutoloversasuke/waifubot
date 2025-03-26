import urllib.request
from pymongo import ReturnDocument
import os
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext

from shivu import application, sudo_users, collection, db, SUPPORT_CHAT, OWNER_ID, user_collection

from telegraph import upload_file
from pyrogram import filters
from shivu import shivuu, collection, CHARA_CHANNEL_ID
from pyrogram.types import InputMediaPhoto
import os

import os
import requests
from shivu import shivuu, collection
from pyrogram import filters


WRONG_FORMAT_TEXT = """Wrong ❌ format...  eg. /upload reply to photo muzan-kibutsuji Demon-slayer 3

format:- /upload reply character-name anime-name rarity-number

use rarity number accordingly rarity Map

rarity_map = {1: "⚪ Common", 2: "🟣 Rare", 3: "🟢 Medium", 4: "🟡 Legendary", 5: "💮 Special Edition", 6: "🔮 Limited Edition", 7: "🎐 Celestial Beauty", 8: "🪽 Divine Edition", 9: "💦 Wet Elegance", 10: "🎴 Cosplay"}
"""


# Define the channel ID and rarity map
rarity_map = {1: "⚪ Common", 2: "🟣 Rare", 3: "🟢 Medium", 4: "🟡 Legendary", 5: "💮 Special Edition", 6: "🔮 Limited Edition", 7: "🎐 Celestial Beauty", 8: "🪽 Divine Edition", 9: "💦 Wet Elegance", 10: "🎴 Cosplay"}

from asyncio import Lock

# Global set to keep track of active IDs and a lock for safe access
active_ids = set()
id_lock = Lock()
import requests

def upload_to_catbox(file_path):
    url = "https://catbox.moe/user/api.php"
    # Set the payload to specify that the upload type is a file and choose the `fileupload` option
    payload = {
        'reqtype': 'fileupload',
    }
    # Open the file in binary mode and send it to Catbox
    files = {
        'fileToUpload': open(file_path, 'rb'),
    }
    # Send the POST request to Catbox with the file and payload
    response = requests.post(url, files=files, data=payload)

    # Check if the upload was successful
    if response.status_code == 200:
        return response.text.strip()  # Return the URL of the uploaded image
    else:
        raise Exception(f"Failed to upload to Catbox. Status Code: {response.status_code}")

# Example usage:
# image_url = upload_to_catbox('path_to_your_image.jpg')
# print(image_url)

# Function to find the next available ID for a character
async def find_available_id():
    async with id_lock:  # Ensure only one upload can find and reserve an ID at a time
        cursor = collection.find().sort('id', 1)
        ids = [doc['id'] for doc in await cursor.to_list(length=None)]
        for i in range(1, max(map(int, ids)) + 2):  # +2 to account for the case where the max ID is the last one
            candidate_id = str(i).zfill(2)
            if candidate_id not in ids and candidate_id not in active_ids:
                active_ids.add(candidate_id)
                return candidate_id
        return str(max(map(int, ids)) + 1).zfill(2)  # Return the next available ID

# Command to upload character information
@shivuu.on_message(filters.command(["wadd"]) & filters.user([7756901810, 7640076990, 7885908019, 7378476666]))
async def ul(client, message):
    reply = message.reply_to_message
    if reply and (reply.photo or reply.document):
        args = message.text.split()
        if len(args) != 4:
            await client.send_message(chat_id=message.chat.id, text=WRONG_FORMAT_TEXT)
            return
        
        # Extract character details from the command arguments
        character_name = args[1].replace('-', ' ').title()
        anime = args[2].replace('-', ' ').title()
        rarity = int(args[3])
        
        # Validate rarity value
        if rarity not in rarity_map:
            await message.reply_text("Invalid rarity value. Please use a value between 1 and 10.")
            return
        
        rarity_text = rarity_map[rarity]
        
        try:
            available_id = await find_available_id()

            # Prepare character data
            character = {
                'name': character_name,
                'anime': anime,
                'rarity': rarity_text,
                'id': available_id
            }

            processing_message = await message.reply("<ᴘʀᴏᴄᴇꜱꜱɪɴɢ>....")
            path = await reply.download()

            # Upload image to Catbox
            catbox_url = upload_to_catbox(path)
            character['img_url'] = catbox_url
            
            # Insert character into the database
            await collection.insert_one(character)

            # Send character details to the channel
            await client.send_photo(
                chat_id=CHARA_CHANNEL_ID,
                photo=catbox_url,
                caption=(
                    f"Character Name: {character_name}\n"
                    f"Anime Name: {anime}\n"
                    f"Rarity: {rarity_text}\n"
                    f"ID: {available_id}\n"
                    f"Added by [{message.from_user.first_name}](tg://user?id={message.from_user.id})"
                ),
            )
            await message.reply_text(f'CHARACTER ADDED.... id :- {available_id}')
        
        except Exception as e:
            await message.reply_text(f"Character Upload Unsuccessful. Error: {str(e)}")
        
        finally:
            os.remove(path)  # Clean up the downloaded file
            async with id_lock:
                active_ids.discard(available_id)  # Remove the ID from the active set once done
    else:
        await message.reply_text("Please reply to a photo or document.")


async def updates(update: Update, context: CallbackContext) -> None:
    if str(update.effective_user.id) not in sudo_users:
        await update.message.reply_text('You do not have permission to use this command.')
        return

    try:
        args = context.args
        if len(args) != 3:
            await update.message.reply_text('Incorrect format. Please use: /update id field new_value')
            return

        # Get character by ID
        character = await collection.find_one({'id': args[0]})
        if not character:
            await update.message.reply_text('Character not found.')
            return

        # Check if field is valid
        valid_fields = ['img_url', 'name', 'anime', 'rarity']
        if args[1] not in valid_fields:
            await update.message.reply_text(f'Invalid field. Please use one of the following: {", ".join(valid_fields)}')
            return

        # Update field
        if args[1] in ['name', 'anime']:
            new_value = args[2].replace('-', ' ').title()
        elif args[1] == 'rarity':
            rarity_map = {1: "⚪️ Common", 2: "🟣 Rare", 3: "🟡 Legendary", 4:"💮 Special Edition", 5: "🔮 Limited Edition", 6: "🎐 Celestial"}
            try:
                new_value = rarity_map[int(args[2])]
            except KeyError:
                await update.message.reply_text('Invalid rarity. Please use 1, 2, 3, 4, 5, 6')
                return
        else:
            new_value = args[2]

        await collection.find_one_and_update({'id': args[0]}, {'$set': {args[1]: new_value}})

        # Update character in user_collection
        user_collection.update_one({'_id': update.effective_user.id, 'characters.' + args[0]: {'$exists': True}}, {'$set': {'characters.' + args[0]: {args[1]: new_value}}})

        await update.message.reply_text('Updated Successfully')
    except Exception as e:
        await update.message.reply_text(f'{str(e)}')
        


UPDATES_HANDLER = CommandHandler('wupdate', updates, block=False)
application.add_handler(UPDATES_HANDLER)


@shivuu.on_message(filters.command("wdel") & filters.user([7756901810, 7640076990, 7885908019, 7378476666]))  # Restrict command to specific user
async def delete_character(client, message):
    # Extract character ID from the command
    if len(message.command) != 2:
        await message.reply(f"Usage: `/del <character_id>`\nExample: `/del abc123`")
        return

    char_id = message.command[1]  # Get the character ID as a string

    # Step 1: Delete the character from `anime_characters_lol`
    char_delete_result = await collection.delete_one({"id": char_id})

    # Step 2: Remove the character from users' collections in `user_collection`
    user_documents = await user_collection.find({"characters.id": char_id}).to_list(None)  # Find users with this character

    if user_documents:
        for user_doc in user_documents:
            await user_collection.update_one(
                {"_id": user_doc["_id"]},  # Identify the user
                {"$pull": {"characters": {"id": char_id}}}  # Remove the character from their list
            )

    # Step 3: Provide feedback
    if char_delete_result.deleted_count > 0 or user_documents:
        await message.reply(f"Successfully deleted character with ID `{char_id}` from the database and all user collections.")
    else:
        await message.reply(f"No character found with ID `{char_id}`.")
