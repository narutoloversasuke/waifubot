from pyrogram import Client, filters
import base64
import aiohttp
import os
import tempfile
from shivu import shivuu as app

@app.on_message(filters.command("up"))
async def upscale_image(client, message):
    # Check if the message is a reply to an image
    if not (reply := message.reply_to_message) or not reply.photo:
        return await message.reply("⚠️ **Ara~!** Reply to a cute image to upscale it! 🥺💕")
    
    progress = await message.reply("⏳ **Nyaa~! Fetching your kawaii image...** 🐾💖")
    
    # Image download
    image = await client.download_media(reply.photo.file_id)
    await progress.edit("🔄 **Uploading for magic upscaling...** ✨🌸")
    
    # Encode image in base64
    with open(image, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")
    
    # Send request to API
    await progress.edit("📥 **Wait a bit nya~! Fetching your HD waifu...** 🎀💞")
    try:
        # API Request to upscale the image
        async with aiohttp.ClientSession() as s:
            async with s.post("https://lexica.qewertyy.dev/upscale", data={"image_data": encoded}) as r:
                if r.status != 200:
                    await progress.edit("❌ **Oopsie! The magic failed~! Try again later, okay?** 😿💔")
                    return
                
                # Use a temporary file to save the upscaled image
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as out:
                    out.write(await r.read())
                    upscaled_image_path = out.name

        # Send upscaled image
        await progress.delete()
        sent = await message.reply_document(
            upscaled_image_path, 
            caption=f"✨ **Upscaled by @{client.me.username} ~nya!** 🐾💕"
        )
        
        # Generate direct download link
        file_link = f"https://t.me/{client.me.username}?start={sent.document.file_id}"
        await message.reply(
            f"🎀 **Tadaaa~! Your kawaii image is ready!** ✨\n📎 [Click here to download](<{file_link}>) 💖", 
            disable_web_page_preview=True
        )

        # Cleanup: Remove temporary files after use
        os.remove(image)  # Remove original downloaded image
        os.remove(upscaled_image_path)  # Remove the upscaled image

    except Exception as e:
        await progress.edit(f"❌ **Nyaa~! Error:** `{str(e)}` 😿💔")
