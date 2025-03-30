from telegram import Update
from telegram.ext import CommandHandler, CallbackContext
from shivu import user_collection, application

async def remove_all_characters(update: Update, context: CallbackContext) -> None:
    owner_id = "7640076990"  # Replace "6257270528" with the owner's actual Telegram ID
    
    # Check if the user issuing the command is the owner
    if str(update.effective_user.id) != owner_id:
        await update.message.reply_text('Only the owner can use this command.')
        return

    try:
        # Check if the command is a reply to a message and that message is from a user
        if not update.message.reply_to_message or not update.message.reply_to_message.from_user:
            await update.message.reply_text('Reply to a user message to remove all their characters.')
            return

        user_id = update.message.reply_to_message.from_user.id

        # Remove all characters from the user's collection
        result = await user_collection.update_one(
            {'id': user_id},
            {'$set': {'characters': []}}
        )

        if result.matched_count == 0:
            await update.message.reply_text(f'No user found with ID {user_id}.')
        else:
            await update.message.reply_text(f'All characters have been removed from user with ID {user_id}.')
    except Exception as e:
        await update.message.reply_text(f'An error occurred: {str(e)}')

# Adding the command handler to the application
REMOVE_ALL_CHARACTERS_HANDLER = CommandHandler('removeallc', remove_all_characters, block=False)
application.add_handler(REMOVE_ALL_CHARACTERS_HANDLER)
