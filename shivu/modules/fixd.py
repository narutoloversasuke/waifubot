import logging
from telegram import Update
from telegram.ext import CallbackContext
from shivu import collection, application
import logging
from telegram import Update
from telegram.ext import CallbackContext

import urllib.request
import uuid
import requests
import random
import html
import logging
from pymongo import ReturnDocument
from typing import List
from bson import ObjectId
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import CommandHandler, CallbackContext, CallbackQueryHandler
from datetime import datetime, timedelta

# Assuming these are defined elsewhere in your code
from shivu import db, UPDATE_CHAT, SUPPORT_CHAT, CHARA_CHANNEL_ID, collection, user_collection
from shivu import (application, PHOTO_URL, OWNER_ID,
                    user_collection, top_global_groups_collection, top_global_groups_collection, 
                    group_user_totals_collection)


from collections import defaultdict

async def check_and_fix_duplicate_ids(update: Update, context: CallbackContext) -> None:
    if str(update.effective_user.id) not in PARTNER:
        await update.message.reply_text('Ask My Owner...')
        return

    try:
        # Step 1: Identify all IDs and check for duplicates
        characters_cursor = collection.find({}, {"id": 1})
        id_counts = {}
        duplicates = []

        async for character in characters_cursor:
            character_id = character["id"]
            if character_id in id_counts:
                id_counts[character_id] += 1
                duplicates.append(character_id)
            else:
                id_counts[character_id] = 1

        if not duplicates:
            await update.message.reply_text("No duplicate IDs found.")
            return

        # Step 2: Fix the duplicate IDs
        fixed_count = 0
        for duplicate_id in duplicates:
            # Fetch all characters with the duplicate ID
            duplicate_characters = await collection.find({"id": duplicate_id}).to_list(length=None)

            for i, character in enumerate(duplicate_characters[1:], start=1):
                # Generate a new unique ID
                while True:
                    new_id = f"{duplicate_id}-{i}"  # Example: append index to the ID
                    if not await collection.find_one({"id": new_id}):
                        break

                # Update the document with the new ID
                await collection.update_one({"_id": character["_id"]}, {"$set": {"id": new_id}})
                fixed_count += 1

        await update.message.reply_text(f"Fixed {fixed_count} duplicate IDs by assigning new unique IDs.")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        await update.message.reply_text(f"An error occurred: {str(e)}")

# Add the command handler to the application
application.add_handler(CommandHandler("fixduplicates", check_and_fix_duplicate_ids))
