from telegram.ext import CommandHandler
from telegram import Update
from shivu import user_collection

# Reset balance for a particular user
async def reset_balance(update: Update, context):
    # Check if the command has one argument (user ID)
    if len(context.args) == 1:
        try:
            user_id = int(context.args[0])
            # Update balance to 0 for the given user_id
            result = await user_collection.update_one({'id': user_id}, {'$set': {'balance': 0}})
            
            if result.matched_count:
                await update.message.reply_text(f"✅ Balance for user ID {user_id} has been reset to 0.")
            else:
                await update.message.reply_text(f"⚠️ No user found with ID {user_id}.")
        except ValueError:
            await update.message.reply_text("❌ Please provide a valid user ID.")
    else:
        await update.message.reply_text("❌ Please provide a user ID to reset the balance.")

# Reset balance for all users
async def reset_all_balance(update: Update, context):
    # Only allow specific users (e.g., admins) to run this command
    admin_ids = [8043832960, 6130275861]  # Admin user IDs
    
    if update.effective_user.id not in admin_ids:
        await update.message.reply_text("❌ You don't have permission to reset the balances for all users.")
        return

    # Reset all users' balance to 0
    result = await user_collection.update_many({}, {'$set': {'balance': 0}})
    
    if result.modified_count:
        await update.message.reply_text(f"✅ All user balances have been reset to 0.")
    else:
        await update.message.reply_text("⚠️ No users' balances were updated.")

# Add handlers for the commands
application.add_handler(CommandHandler("resetbal", reset_balance, block=False))
application.add_handler(CommandHandler("resetallbal", reset_all_balance, block=False))
