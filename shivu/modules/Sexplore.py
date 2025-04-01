import random
import asyncio
from datetime import datetime, timedelta
from telegram.ext import CommandHandler, CallbackContext
from shivu import application, user_collection

COOLDOWN_DURATION = 30  # Cooldown in seconds
user_cooldowns = {}

IMAGE_URL = "https://postimg.cc/xJKjGvKn"  # Adventure Image

async def explore(update, context):
    if update.message.chat.type == "private":
        await update.message.reply_text("🚫 *This command only works in group chats!*", parse_mode="Markdown")
        return

    user_id = update.effective_user.id

    if update.message.reply_to_message:
        await update.message.reply_text("⚠ *You can't use this command as a reply!*", parse_mode="Markdown")
        return

    # Cooldown check
    if user_id in user_cooldowns and (datetime.utcnow() - user_cooldowns[user_id]) < timedelta(seconds=COOLDOWN_DURATION):
        remaining_time = int((timedelta(seconds=COOLDOWN_DURATION) - (datetime.utcnow() - user_cooldowns[user_id])).total_seconds())
        await update.message.reply_text(f"⏳ *Patience, young explorer...* You must wait `{remaining_time}` seconds before venturing again!", parse_mode="Markdown")
        return

    # Fetch user balance
    user_data = await user_collection.find_one({'id': user_id}, projection={'balance': 1})
    balance = user_data.get('balance', 0)
    explore_cost = 500  

    if balance < explore_cost:
        await update.message.reply_text("❌ *Insufficient energy!* You need at least *500 tokens* to explore! 🔥", parse_mode="Markdown")
        return

    # Deduct exploration fee
    await user_collection.update_one({'id': user_id}, {'$inc': {'balance': -explore_cost}})

    # **Step 1: Send "Exploring..." Message**
    exploring_message = await update.message.reply_text(
        "🔍 *Venturing into the unknown...*\n"
        "👣 You step into a mysterious path... What awaits you? 🤔", 
        parse_mode="Markdown"
    )

    # **Step 2: Simulate Time Passing (Suspense Effect)**
    await asyncio.sleep(random.randint(2, 4))  

    # Adventure Outcome (40% Win, 60% Loss)
    win_chance = random.randint(1, 100)

    if win_chance <= 40:  # 40% Win Rate
        reward = random.randint(8000, 10125)
        result_message = (
            f"✨ *Your waifu guided you through the shadows...* 🌙\n"
            f"🎭 You uncovered *a legendary hidden treasure*! 🏆\n"
            f"💰 **Reward:** `{reward}` Tokens! 🎉"
        )
    else:  # 60% Loss Rate
        loss = random.randint(200, 500)
        result_message = (
            f"💀 *Trapped in a cursed labyrinth...* 🕸️\n"
            f"⚠ Your waifu tried to warn you, but it was *too late*! 😱\n"
            f"🩸 You barely escaped with `{loss}` Tokens… and a heart full of regret."
        )
        reward = loss

    await user_collection.update_one({'id': user_id}, {'$inc': {'balance': reward}})
    
    user_cooldowns[user_id] = datetime.utcnow()

    # **Step 3: Try Sending Image (Retry if Fails)**
    try:
        await exploring_message.delete()  # Remove "Exploring..." Message
        await update.message.reply_photo(photo=IMAGE_URL, caption=result_message, parse_mode="Markdown")
    except:
        await update.message.reply_text(result_message, parse_mode="Markdown")

    context.job_queue.run_once(clear_cooldown, COOLDOWN_DURATION, context=user_id)

async def clear_cooldown(context: CallbackContext):
    user_id = context.job.context
    user_cooldowns.pop(user_id, None)

application.add_handler(CommandHandler("explore", explore, block=True))
