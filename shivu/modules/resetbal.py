import random
import math
from telegram.ext import CommandHandler, CallbackContext
from shivu import application, user_collection
from datetime import datetime, timedelta

COOLDOWN_DURATION = 30
COMMAND_BAN_DURATION = 600

last_command_time = {}
user_cooldowns = {}

# Command to reset a specific user's balance
async def reset_balance(update, context):
    if len(context.args) != 1:
        await update.message.reply_text("⚠️ Usage: `/resetbal <user_id>`", parse_mode="Markdown")
        return

    target_user_id = context.args[0]

    if target_user_id not in ["6130275861", "8043832960"]:
        await update.message.reply_text("❌ You don't have permission to reset this user's balance.")
        return

    target_user_id = int(target_user_id)
    user_data = await user_collection.find_one({'id': target_user_id})

    if not user_data:
        await update.message.reply_text(f"⚠️ No user found with ID `{target_user_id}`.", parse_mode="Markdown")
        return

    await user_collection.update_one({'id': target_user_id}, {'$set': {'balance': 0, 'loan': 0}})

    await update.message.reply_text(f"✅ Balance and Loan for user `{target_user_id}` have been successfully reset.", parse_mode="Markdown")

# Command to reset balance for all users
async def reset_all_balances(update, context):
    admin_id = update.effective_user.id
    if admin_id not in [6130275861, 8043832960]:  # Only allow these IDs to reset all balances
        await update.message.reply_text("❌ You do not have permission to reset all balances.")
        return

    await user_collection.update_many({}, {'$set': {'balance': 0, 'loan': 0}})
    await update.message.reply_text("✅ All users' balances and loans have been reset successfully.")

application.add_handler(CommandHandler("bal", balance, block=False))
application.add_handler(CommandHandler("resetbal", reset_balance, block=False))
application.add_handler(CommandHandler("resetallbal", reset_all_balances, block=False))
