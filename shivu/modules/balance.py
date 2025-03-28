import random
import math
from telegram.ext import CommandHandler, CallbackContext
from shivu import application, user_collection
from datetime import datetime, timedelta

COOLDOWN_DURATION = 30
COMMAND_BAN_DURATION = 600

last_command_time = {}
user_cooldowns = {}

async def check_balance(user_id, required_balance):
    user_data = await user_collection.find_one({'id': user_id}, projection={'balance': 1})
    user_balance = user_data.get('balance', 0)
    if user_balance < required_balance:
        return False
    return True

async def balance(update, context):
    user_id = update.effective_user.id
    user_data = await user_collection.find_one({'id': user_id})
    
    if user_data:
        balance_amount = user_data.get('balance', 0)
        tokens_amount = user_data.get('tokens', 0)
        balance_message = f"Your Current Balance Is :\nGold Coins: `{balance_amount}`\nTokens: `{tokens_amount}`"
    else:
        balance_message = "You are not eligible To be a Hunter 🍂"
        
    await update.message.reply_text(balance_message)

async def random_daily_reward(update, context):
    if update.message.chat.type == "private":
        await update.message.reply_text("This command can only be used in group chats.")
        return

    user_id = update.effective_user.id

    if update.message.reply_to_message:
        await update.message.reply_text("This command cannot be used as a reply to someone else's message.")
        return

    if user_id in user_cooldowns and (datetime.utcnow() - user_cooldowns[user_id]) < timedelta(seconds=COOLDOWN_DURATION):
        remaining_time = COOLDOWN_DURATION - (datetime.utcnow() - user_cooldowns[user_id]).total_seconds()
        await update.message.reply_text(f"You must wait {int(remaining_time)} seconds before using /explore again.")
        return

    crime_fee = 300
    if not await check_balance(user_id, crime_fee):
        await update.message.reply_text("You need at least 300 Gold coins to use /explore.")
        return

    await user_collection.update_one({'id': user_id}, {'$inc': {'balance': -crime_fee}})

    random_reward = random.randint(8000, 10125)

    congratulatory_messages = ["Explore a dungeon", "Explore a dark forest", "Explore ruins", "Explore an elvish village", "Explore a goblin nest", "Explore an orc den"]
    random_message = random.choice(congratulatory_messages)

    await user_collection.update_one(
        {'id': user_id},
        {'$inc': {'tokens': random_reward}}
    )
    last_command_time[user_id] = datetime.utcnow()

    user_cooldowns[user_id] = datetime.utcnow()

    await update.message.reply_text(f"You {random_message} and got {random_reward} Tokens.🤫")

async def clear_command_ban(context: CallbackContext):
    user_id = context.job.context
    if user_id in user_cooldowns:
        del user_cooldowns[user_id]

async def mtop(update, context):
    top_users = await user_collection.find({}, projection={'id': 1, 'first_name': 1, 'last_name': 1, 'balance': 1}).sort('balance', -1).limit(10).to_list(10)

    top_users_message = "Top 10 Rich Hunters data.\n\n"
    for i, user in enumerate(top_users, start=1):
        first_name = user.get('first_name', 'Unknown')
        last_name = user.get('last_name', '')
        user_id = user.get('id', 'Unknown')

        full_name = f"{first_name} {last_name}" if last_name else first_name

        top_users_message += f"{i}. <a href='tg://user?id={user_id}'>{full_name}</a>, $ `{user.get('balance', 0)}` Gold Coins\n"

    photo_path = 'https://telegra.ph/file/07283c3102ae87f3f2833.png'
    await update.message.reply_photo(photo=photo_path, caption=top_users_message, parse_mode='HTML')

async def daily_reward(update, context):
    user_id = update.effective_user.id
    user_data = await user_collection.find_one({'id': user_id}, projection={'last_daily_reward': 1, 'balance': 1})

    if user_data:
        last_claimed_date = user_data.get('last_daily_reward')

        if last_claimed_date and last_claimed_date.date() == datetime.utcnow().date():
            remaining_time = timedelta(days=1) - (datetime.utcnow() - last_claimed_date)
            formatted_time = await format_time_delta(remaining_time)
            await update.message.reply_text(f"Soory ! hunter but you already claimed . Next reward in: `{formatted_time}`.")
            return

    await user_collection.update_one(
        {'id': user_id},
        {'$inc': {'balance': 2000}, '$set': {'last_daily_reward': datetime.utcnow()}}
    )

    await update.message.reply_text("Congratulations! You claim $ `2000` Gold coins as a daily reward.")

async def format_time_delta(delta):
    seconds = delta.total_seconds()
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours)}h {int(minutes)}m {int(seconds)}s"

async def roll(update, context):
    user_id = update.effective_user.id
    try:
        amount = int(context.args[0])
        choice = context.args[1].upper()
    except (IndexError, ValueError):
        await update.message.reply_text("Invalid usage, please use /roll <amount> <ODD/EVEN>")
        return

    if amount < 0:
        await update.message.reply_text("Amount must be positive.")
        return

    user_data = await user_collection.find_one({'id': user_id})
    if not user_data:
        await update.message.reply_text("User data not found.")
        return

    balance_amount = user_data.get('balance', 0)
    if amount < balance_amount * 0.07:
        await update.message.reply_text("You can bet more than 7% of your balance.")
        return

    if balance_amount < amount:
        await update.message.reply_text("Insufficient balance to place the bet.")
        return

    dice_message = await context.bot.send_dice(update.effective_chat.id, "🎲")
    dice_value = dice_message.dice.value

    dice_result = "ODD" if dice_value % 2 != 0 else "EVEN"

    xp_change = 0

    if choice == dice_result:
        xp_change = 4
        await user_collection.update_one(
            {'id': user_id},
            {'$inc': {'balance': amount, 'user_xp': xp_change}}
        )
        await update.message.reply_text(f"Dice roll: {dice_value}\nYou won! Your balance increased by {amount * 2}.")
    else:
        xp_change = -2
        await user_collection.update_one(
            {'id': user_id},
            {'$inc': {'balance': -amount, 'user_xp': xp_change}}
        )
        await update.message.reply_text(f"Dice roll: {dice_value}\nYou lost! {amount} deducted from your balance.")

    await update.message.reply_text(f"XP change: {xp_change}")

async def xp(update, context):
    user_id = update.effective_user.id
    user_data = await user_collection.find_one({'id': user_id})

    if not user_data:
        await update.message.reply_text("User data not found.")
        return

    xp = user_data.get('user_xp', 0)
    level = math.floor(math.sqrt(xp / 100)) + 1

    if level > 100:
        level = 100

    ranks = {1: "E", 10: "D", 30: "C", 50: "B", 70: "A", 90: "S"}
    rank = next((rank for xp_limit, rank in ranks.items() if level <= xp_limit), None)

    message = f"Your current level is `{level}`\nand your rank is `{rank}`."

    await update.message.reply_text(message)

application.add_handler(CommandHandler("roll", roll, block=False))
application.add_handler(CommandHandler("xp", xp, block=False))
application.add_handler(CommandHandler("bal", balance, block=False))
application.add_handler(CommandHandler("pay", pay, block=False))
application.add_handler(CommandHandler("Tophunters", mtop, block=False))
application.add_handler(CommandHandler("claim", daily_reward, block=False))
application.add_handler(CommandHandler("explore", random_daily_reward, block=True))

