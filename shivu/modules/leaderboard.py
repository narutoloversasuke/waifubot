import os
import random
import html

from telegram import Update
from telegram.ext import CommandHandler, CallbackContext

from shivu import (application, OWNER_ID,
                   user_collection, top_global_groups_collection,
                   group_user_totals_collection)

from shivu import sudo_users as SUDO_USERS 

PHOTO_URL = [
    "https://i.postimg.cc/H8C3P7XC/image1.jpg",
    "https://i.postimg.cc/JGVS9sM0/image2.jpg",
    "https://i.postimg.cc/2VDX0g7B/image3.jpg"
]

async def global_leaderboard(update: Update, context: CallbackContext) -> None:
    cursor = top_global_groups_collection.aggregate([
        {"$project": {"group_name": 1, "count": 1}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ])
    leaderboard_data = await cursor.to_list(length=10)

    leaderboard_message = "<b>⚔️ LEGENDS OF THE ARENA ⚔️</b>\n"
    leaderboard_message += "🔥 These are the **TOP 10 GROUPS** that have proven their might!\n\n"
    
    for i, group in enumerate(leaderboard_data, start=1):
        group_name = html.escape(group.get('group_name', 'Unknown'))[:15] + ('...' if len(group.get('group_name', 'Unknown')) > 15 else '')
        count = group['count']
        leaderboard_message += f'🏆 {i}. <b>{group_name}</b> ➾ **{count} Battles Won**\n'

    await update.message.reply_photo(photo=random.choice(PHOTO_URL), caption=leaderboard_message, parse_mode='HTML')

async def ctop(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id
    cursor = group_user_totals_collection.aggregate([
        {"$match": {"group_id": chat_id}},
        {"$project": {"username": 1, "first_name": 1, "character_count": "$count"}},
        {"$sort": {"character_count": -1}},
        {"$limit": 10}
    ])
    leaderboard_data = await cursor.to_list(length=10)

    leaderboard_message = "<b>🔥 THE ELITE WARRIORS 🔥</b>\n"
    leaderboard_message += "💪 These are the **TOP 10 CHAMPIONS** of this group!\n\n"
    
    for i, user in enumerate(leaderboard_data, start=1):
        first_name = html.escape(user.get('first_name', 'Unknown'))[:15] + ('...' if len(user.get('first_name', 'Unknown')) > 15 else '')
        username = user.get('username')
        user_link = f'<a href="https://t.me/{username}"><b>{first_name}</b></a>' if username else f'<b>{first_name}</b>'
        character_count = user['character_count']
        leaderboard_message += f'🥇 {i}. {user_link} ➾ **{character_count} Enemies Defeated**\n'

    await update.message.reply_photo(photo=random.choice(PHOTO_URL), caption=leaderboard_message, parse_mode='HTML')

async def leaderboard(update: Update, context: CallbackContext) -> None:
    cursor = user_collection.aggregate([
        {"$project": {"username": 1, "first_name": 1, "character_count": {"$size": "$characters"}}},
        {"$sort": {"character_count": -1}},
        {"$limit": 10}
    ])
    leaderboard_data = await cursor.to_list(length=10)

    leaderboard_message = "<b>🏅 THE CHOSEN ONES 🏅</b>\n"
    leaderboard_message += "🌟 These are the **TOP 10 WARRIORS** who have claimed the most victories!\n\n"
    
    for i, user in enumerate(leaderboard_data, start=1):
        first_name = html.escape(user.get('first_name', 'Unknown'))[:15] + ('...' if len(user.get('first_name', 'Unknown')) > 15 else '')
        username = user.get('username')
        user_link = f'<a href="https://t.me/{username}"><b>{first_name}</b></a>' if username else f'<b>{first_name}</b>'
        character_count = user['character_count']
        leaderboard_message += f'👑 {i}. {user_link} ➾ **{character_count} Legendary Wins**\n'

    await update.message.reply_photo(photo=random.choice(PHOTO_URL), caption=leaderboard_message, parse_mode='HTML')

async def stats(update: Update, context: CallbackContext) -> None:
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("🚫 You lack the power to access these stats!")
        return

    user_count = await user_collection.count_documents({})
    group_count = len(await group_user_totals_collection.distinct('group_id'))

    await update.message.reply_text(f'📊 **Total Warriors**: {user_count}\n🏰 **Total Battlefields (Groups)**: {group_count}')

async def send_users_document(update: Update, context: CallbackContext) -> None:
    if str(update.effective_user.id) not in SUDO_USERS:
        await update.message.reply_text('❌ Only for the supreme overlords (Sudo Users).')
        return

    cursor = user_collection.find({})
    users = [document async for document in cursor]
    
    with open('users.txt', 'w') as f:
        f.write("\n".join(user['first_name'] for user in users if 'first_name' in user))

    with open('users.txt', 'rb') as f:
        await context.bot.send_document(chat_id=update.effective_chat.id, document=f)

    os.remove('users.txt')

async def send_groups_document(update: Update, context: CallbackContext) -> None:
    if str(update.effective_user.id) not in SUDO_USERS:
        await update.message.reply_text('❌ Only for the supreme overlords (Sudo Users).')
        return

    cursor = top_global_groups_collection.find({})
    groups = [document async for document in cursor]

    with open('groups.txt', 'w') as f:
        f.write("\n".join(group['group_name'] for group in groups if 'group_name' in group))

    with open('groups.txt', 'rb') as f:
        await context.bot.send_document(chat_id=update.effective_chat.id, document=f)

    os.remove('groups.txt')

application.add_handler(CommandHandler('ctop', ctop, block=False))
application.add_handler(CommandHandler('stats', stats, block=False))
application.add_handler(CommandHandler('TopGroups', global_leaderboard, block=False))
application.add_handler(CommandHandler('list', send_users_document, block=False))
application.add_handler(CommandHandler('groups', send_groups_document, block=False))
application.add_handler(CommandHandler('top', leaderboard, block=False))
