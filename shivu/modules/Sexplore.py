import random
from telegram.ext import CommandHandler, CallbackContext
from shivu import application, user_collection
from datetime import datetime, timedelta

COOLDOWN_DURATION = 30
COMMAND_BAN_DURATION = 600

last_command_time = {}
user_cooldowns = {}

# Image link provided by you
image_link = "https://postimg.cc/xJKjGvKn"

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
        await update.message.reply_text(f"⏳ *Patience, young explorer...* You must wait `{int(remaining_time)}` seconds before venturing again!")
        return

    user_data = await user_collection.find_one({'id': user_id}, projection={'balance': 1})
    user_balance = user_data.get('balance', 0)
    crime_fee = 300

    if user_balance < crime_fee:
        await update.message.reply_text("❌ *Insufficient energy!* You need at least *500 tokens* to explore! 🔥")
        return

    await user_collection.update_one({'id': user_id}, {'$inc': {'balance': -crime_fee}})

    win_chance = random.randint(1, 100)
    
    if win_chance <= 40:  # 40% chance to win
        random_reward = random.randint(8000, 10125)
        result_message = (
            f"✨ *Your waifu guided you through the shadows...* 🌙\n"
            f"🎭 You uncovered *a legendary hidden treasure*! 🏆\n"
            f"💰 **Reward:** `{random_reward}` Tokens! 🎉"
        )
        await user_collection.update_one({'id': user_id}, {'$inc': {'balance': random_reward}})
    else:  # 60% chance to lose
        random_reward = random.randint(200, 500)
        result_message = (
            f"💀 *Trapped in a cursed labyrinth...* 🕸️\n"
            f"⚠ Your waifu tried to warn you, but it was *too late*! 😱\n"
            f"🩸 You barely escaped with `{random_reward}` Tokens… and a heart full of regret."
        )
        await user_collection.update_one({'id': user_id}, {'$inc': {'balance': random_reward}})
    
    last_command_time[user_id] = datetime.utcnow()
    user_cooldowns[user_id] = datetime.utcnow()

    await update.message.reply_photo(photo=image_link, caption=result_message, parse_mode="Markdown")

async def clear_command_ban(context: CallbackContext):
    user_id = context.job.context
    if user_id in user_cooldowns:
        del user_cooldowns[user_id]

application.add_handler(CommandHandler("explore", random_daily_reward, block=True))
