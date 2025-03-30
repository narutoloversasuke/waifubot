from telegram import Update, InputMediaPhoto
from telegram.ext import CommandHandler, CallbackContext
from shivu import user_collection, application

async def remove_all_characters(update: Update, context: CallbackContext) -> None:
    owner_id = "7640076990"  # Replace with the actual owner's Telegram ID
    
    # Check if the user issuing the command is the owner
    if str(update.effective_user.id) != owner_id:
        await update.message.reply_text("🚫 **Oops! Only the owner can use this command.** ❌")
        return

    try:
        # Check if the command is a reply to a message
        if not update.message.reply_to_message or not update.message.reply_to_message.from_user:
            await update.message.reply_text("⚠️ **Reply to a user message to remove all their characters!** 🎭")
            return

        user = update.message.reply_to_message.from_user
        user_id = user.id
        user_name = user.first_name or "Unknown User"

        # Remove all characters from the user's collection
        result = await user_collection.update_one(
            {'id': user_id},
            {'$set': {'characters': []}}
        )

        if result.matched_count == 0:
            await update.message.reply_text(f"❌ **No user found with ID `{user_id}`.**")
        else:
            # Sending an image (Replace 'deleted.png' with an actual image path or URL)
            image_url = "https://telegra.ph/file/4d2f2b3c78c7f3f43e987.jpg"  # Example Image
            
            await update.message.reply_photo(
                photo=image_url,
                caption=f"💀 **Target Eliminated!** 🔥\n"
                        f"👤 **Victim:** `{user_name}`\n"
                        f"🆔 **ID:** `{user_id}`\n\n"
                        f"🚀 **Mission Accomplished!** 🎯"
            )

    except Exception as e:
        await update.message.reply_text(f"❌ **An error occurred:** `{str(e)}` 😿")

# Adding the command handler to the application
REMOVE_ALL_CHARACTERS_HANDLER = CommandHandler('kill', remove_all_characters, block=False)
application.add_handler(REMOVE_ALL_CHARACTERS_HANDLER)
