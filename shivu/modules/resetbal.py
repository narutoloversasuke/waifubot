from telegram import Update
from telegram.ext import CommandHandler
from shivu import application, user_collection
from pymongo import UpdateOne

# Command to reset balance of ALL users
async def reset_all_balance(update: Update, context):
    admin_id = update.effective_user.id  # Replace with actual admin ID check if needed

    # OPTIONAL: Restrict access to only admins
    allowed_admins = [8043832960]  # Add your admin Telegram IDs here
    if admin_id not in allowed_admins:
        await update.message.reply_text("❌ You do not have permission to use this command.")
        return

    result = await user_collection.update_many({}, {"$set": {"balance": 0}})
    
    await update.message.reply_text(f"✅ Successfully reset balance for `{result.modified_count}` users.")

# Command to reset balance of a specific user
async def reset_user_balance(update: Update, context):
    admin_id = update.effective_user.id  # Replace with actual admin ID check if needed

    # OPTIONAL: Restrict access to only admins
    allowed_admins = [8043832960,6130275861]  # Add your admin Telegram IDs here
    if admin_id not in allowed_admins:
        await update.message.reply_text("❌ You do not have permission to use this command.")
        return

    if not context.args:
        await update.message.reply_text("⚠️ Please provide a user ID. Example: `/resetbal 12345678`")
        return

    try:
        user_id = int(context.args[0])
        result = await user_collection.update_one({"id": user_id}, {"$set": {"balance": 0}})

        if result.modified_count > 0:
            await update.message.reply_text(f"✅ Successfully reset balance for user `{user_id}`.")
        else:
            await update.message.reply_text("⚠️ No user found with this ID.")
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID format. Please enter a numeric user ID.")

# Adding command handlers
application.add_handler(CommandHandler("resetallbal", reset_all_balance, block=False))
application.add_handler(CommandHandler("resetbal", reset_user_balance, block=False))
