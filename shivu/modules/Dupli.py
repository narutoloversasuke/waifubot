from pyrogram import filters
from pyrogram.types import Message
from collections import Counter
from shivu import shivuu as app

# Function to generate a new unique id
import asyncio
from pyrogram import Client, filters
from shivu import collection



async def find_available_id(existing_ids):
    """Find an available ID that is not in the existing IDs."""
    max_id = max(map(int, existing_ids), default=0)  # Get the max ID or 0 if no IDs exist
    for i in range(1, max_id + 2):  # Check up to max_id + 1
        new_id = str(i).zfill(2)
        if new_id not in existing_ids:
            return new_id
    return str(max_id + 1).zfill(2)  # Return the next available ID

async def update_duplicate_ids():
    """Find and update duplicate IDs with new available IDs."""
    # Step 1: Fetch all documents and collect their IDs
    cursor = collection.find({})
    documents = await cursor.to_list(length=None)
    
    id_count = {}
    for doc in documents:
        id = doc.get('id')
        if id:
            if id not in id_count:
                id_count[id] = []
            id_count[id].append(doc)
    
    # Step 2: Identify duplicates
    duplicates = [docs for id, docs in id_count.items() if len(docs) > 1]

    for duplicate_docs in duplicates:
        existing_ids = set(doc['id'] for doc in duplicate_docs)
        for doc in duplicate_docs[1:]:  # Skip the first document, which will retain its ID
            new_id = await find_available_id(existing_ids)
            existing_ids.add(new_id)  # Add new ID to existing IDs set to avoid collision
            await collection.update_one({'_id': doc['_id']}, {'$set': {'id': new_id}})
            print(f"Updated document with _id {doc['_id']} to new id {new_id}")

@app.on_message(filters.command("fdupli"))  # Ensure only sudo users can run this
async def handle_fdupli_command(client, message):
    try:
        await update_duplicate_ids()
        await message.reply("Duplicate IDs have been updated successfully.")
    except Exception as e:
        print(f"Error: {e}")
        await message.reply("An error occurred while updating duplicate IDs.")
