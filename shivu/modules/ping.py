import time
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext
from shivu import application, sudo_users

async def ping(update: Update, context: CallbackContext) -> None:
    if str(update.effective_user.id) not in sudo_users:
        await update.message.reply_text("❌ This command is for Sudo users only!")
        return

    start_time = time.time()
    
    # Sending initial message with an image
    message = await update.message.reply_photo(
        photo="https://graph.org/file/6dbdd7fb645d0c2e19b09-4b7ef51823c0f617f2.jpg",  # Your Image
        caption="🛰️ **Pinging...** 🚀"
    )

    end_time = time.time()
    elapsed_time = round((end_time - start_time) * 1000, 2)

    # Updating message with stylish ping response
    await message.edit_caption(
        caption=f"🏓 **Pong!**\n⏳ **Response Time:** `{elapsed_time}ms`\n⚡ **Speed:** Ultra Fast!"
    )

application.add_handler(CommandHandler("ping", ping))
