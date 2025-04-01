import random
import asyncio
from datetime import datetime, timedelta
from telegram.ext import CommandHandler, CallbackContext
from shivu import application, user_collection

# Constants
LOAN_LIMIT = 400000  # Max loan amount (4 Lakh tokens)
LOAN_DURATION = 7  # Loan repayment period in days
user_cooldowns = {}

# Loan Command
async def loan(update, context):
    user_id = update.effective_user.id
    if update.message.reply_to_message:
        await update.message.reply_text("⚠ *You can't use this command as a reply!*", parse_mode="Markdown")
        return

    # Fetch user balance and loan data
    user_data = await user_collection.find_one({'id': user_id}, projection={'balance': 1, 'loan': 1, 'loan_taken_at': 1})
    balance = user_data.get('balance', 0)
    existing_loan = user_data.get('loan', 0)
    loan_taken_at = user_data.get('loan_taken_at', None)

    # Check if the user already has an active loan
    if existing_loan > 0:
        await update.message.reply_text(f"❌ *You already have an active loan of {existing_loan} tokens!* You need to repay it before taking a new loan.", parse_mode="Markdown")
        return

    try:
        loan_amount = int(context.args[0])  # Get the loan amount from the command argument
    except (IndexError, ValueError):
        await update.message.reply_text("❌ *Please specify the loan amount!* Example: `/loan 1000`", parse_mode="Markdown")
        return

    if loan_amount <= 0:
        await update.message.reply_text("❌ *Loan amount should be greater than zero!*", parse_mode="Markdown")
        return

    if loan_amount > LOAN_LIMIT:
        await update.message.reply_text(f"❌ *Loan amount exceeds the limit of {LOAN_LIMIT} tokens!*", parse_mode="Markdown")
        return

    # Update the user's balance and set loan
    await user_collection.update_one({'id': user_id}, {
        '$inc': {'balance': loan_amount}, 
        '$set': {'loan': loan_amount, 'loan_taken_at': datetime.utcnow()}
    })

    # Send loan success message
    await update.message.reply_text(f"💰 *You have successfully taken a loan of {loan_amount} tokens!* Your balance is now: `{balance + loan_amount}` tokens. Please repay within {LOAN_DURATION} days.", parse_mode="Markdown")


# Loan Repayment Command
async def repay(update, context):
    user_id = update.effective_user.id
    if update.message.reply_to_message:
        await update.message.reply_text("⚠ *You can't use this command as a reply!*", parse_mode="Markdown")
        return

    # Fetch user data
    user_data = await user_collection.find_one({'id': user_id}, projection={'balance': 1, 'loan': 1, 'loan_taken_at': 1})
    balance = user_data.get('balance', 0)
    loan_amount = user_data.get('loan', 0)
    loan_taken_at = user_data.get('loan_taken_at', None)

    if loan_amount == 0:
        await update.message.reply_text("❌ *You don't have any active loan to repay!*", parse_mode="Markdown")
        return

    # Check if loan duration has passed (7 days)
    if datetime.utcnow() - loan_taken_at > timedelta(days=LOAN_DURATION):
        await update.message.reply_text(f"❌ *You failed to repay your loan within {LOAN_DURATION} days!* Your remaining loan balance will be deducted from your account.", parse_mode="Markdown")
        
        # Deduct the remaining loan balance from the user's account
        await user_collection.update_one({'id': user_id}, {'$inc': {'balance': -loan_amount}, '$set': {'loan': 0}})
        await update.message.reply_text(f"💸 *Your remaining loan of {loan_amount} tokens has been deducted from your account.*", parse_mode="Markdown")
        return

    try:
        repay_amount = int(context.args[0])  # Get the repay amount from the command argument
    except (IndexError, ValueError):
        await update.message.reply_text("❌ *Please specify the amount you want to repay!* Example: `/repay 500`", parse_mode="Markdown")
        return

    if repay_amount <= 0:
        await update.message.reply_text("❌ *Repay amount must be greater than zero!*", parse_mode="Markdown")
        return

    if repay_amount > balance:
        await update.message.reply_text(f"❌ *Insufficient balance!* You have only `{balance}` tokens.", parse_mode="Markdown")
        return

    if repay_amount < loan_amount:
        await update.message.reply_text(f"⚠ *Partial repayment accepted.* Your remaining loan balance: `{loan_amount - repay_amount}` tokens.", parse_mode="Markdown")

    # Deduct repay amount and clear loan if fully repaid
    await user_collection.update_one({'id': user_id}, {'$inc': {'balance': -repay_amount}, '$set': {'loan': max(0, loan_amount - repay_amount)}})

    # Success repayment message
    await update.message.reply_text(f"💸 *Repayment of {repay_amount} tokens successful!* Your new balance: `{balance - repay_amount}` tokens.", parse_mode="Markdown")


# Registering commands
application.add_handler(CommandHandler("loan", loan, block=True))
application.add_handler(CommandHandler("repay", repay, block=True))
