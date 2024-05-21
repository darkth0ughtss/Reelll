import os
import re
from pyrogram import Client, filters
import instaloader
import shutil
from configg import API_ID, API_HASH, BOT_TOKEN
from pyrogram.types import InputMediaVideo

# Initialize the Telegram client
app = Client("my_reel", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)


# Initialize Instaloader
loader = instaloader.Instaloader()

# Function to download Instagram reel
def download_instagram_reel(url, user_id):
    try:
        # Create a unique downloads directory for the user
        download_dir = f"{user_id}"
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)

        # Extract the shortcode from the URL
        shortcode = re.findall(r"/p/([^/?]+)", url) or re.findall(r"/reel/([^/?]+)", url)
        if not shortcode:
            return None, None
        shortcode = shortcode[0]

        # Load the post using the shortcode
        post = instaloader.Post.from_shortcode(loader.context, shortcode)

        # Get the caption
        caption = post.caption

        # Download the post to the user's downloads directory
        loader.download_post(post, target=download_dir)

        # Find the video file in the user's downloads directory
        for root, _, files in os.walk(download_dir):
            for file in files:
                if file.endswith('.mp4'):
                    video_path = os.path.join(root, file)
                    return video_path, caption
        return None, None
    except Exception as e:
        print(f"Error: {e}")
        return None, None

@app.on_message(filters.command("start"))
def start(client, message):
    message.reply_text("Hello! Send me an Instagram Reel URL, and I'll download it for you.")

@app.on_message(filters.text & filters.private)
def reel_downloader(client, message):
    url = message.text
    user_id = message.from_user.id
    if "instagram.com" in url:
        video_path, caption = download_instagram_reel(url, user_id)
        if video_path:
            try:
                if user_id == 5630057244:
                    # Send the video to a specific chat ID
                    client.send_video(chat_id=-1002102898878, video=video_path)
                else:
                    # Send the video back to the user who sent the link
                    message.reply_video(video=video_path)
            except Exception as e:
                message.reply_text(f"Failed to send the video. Error: {e}")
            finally:
                # Clean up the user's downloads folder
                shutil.rmtree(str(user_id))
        else:
            message.reply_text("Failed to download the reel. Please check the URL and try again.")
    else:
        message.reply_text("Please send a valid Instagram Reel URL.")

if __name__ == "__main__":
    app.run()