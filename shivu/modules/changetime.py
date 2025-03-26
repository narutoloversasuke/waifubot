from pymongo import ReturnDocument
from pyrogram.enums import ChatMemberStatus, ChatType
from shivu import user_totals_collection, shivuu
from pyrogram import Client, filters
from pyrogram.types import Message

ADMINS = [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]

@shivuu.on_message(filters.command("changetime"))
async def change_time(client: Client, message: Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    member = await shivuu.get_chat_member(chat_id, user_id)

    if member.status not in ADMINS:
        await message.reply_text("⛔ You lack the authority to alter the sacred timeline!")
        return

    try:
        args = message.command
        if len(args) != 2:
            await message.reply_text("📜 The cosmic scripts demand a valid command: `/changetime <number>`")
            return

        new_frequency = int(args[1])
        if new_frequency < 100:
            await message.reply_text("⚠️ The ancient laws forbid frequencies below 100!")
            return

        chat_frequency = await user_totals_collection.find_one_and_update(
            {"chat_id": str(chat_id)},
            {"$set": {"message_frequency": new_frequency}},
            upsert=True,
            return_document=ReturnDocument.AFTER
        )

        await message.reply_text(f"✅ The flow of time has been rewritten! New frequency: **{new_frequency}**")
    except ValueError:
        await message.reply_text("❌ The cosmic energies reject invalid numbers! Use digits only.")
    except Exception as e:
        await message.reply_text(f"⚠️ A disturbance in the timeline! Error: `{str(e)}`")
