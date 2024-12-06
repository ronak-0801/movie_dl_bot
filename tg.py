import aiohttp
import asyncio
from bs4 import BeautifulSoup
import ssl
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import os
from dotenv import load_dotenv

load_dotenv()
# Configure logging
logging.basicConfig(level=logging.INFO)

# Telegram bot token (replace with your bot token)
TOKEN = os.getenv('TOKEN')

# Function to search torrents asynchronously
async def search_torrent(query):
    url = f'https://www.1337x.to/search/{query}/1/'
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    

# Function to get magnet link asynchronously
async def get_torrent1337x(links):
    torrent_links = []
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    async with aiohttp.ClientSession() as session:
        for link in links:
            for attempt in range(3):  # Retry up to 3 times
                try:
                    async with session.get(link, ssl=ssl_context) as req:
                        response_text =  req.text()
                        soup = BeautifulSoup(response_text, 'html.parser')
                        page_content = soup.find('div', class_="col-9 page-content")
                        magnet_link_tag = page_content.find('li').find('a', href=True)

                        if magnet_link_tag and 'magnet:' in magnet_link_tag['href']:
                            torrent_links.append(magnet_link_tag['href'])
                        else:
                            torrent_links.append(None)
                        break
                except aiohttp.ClientConnectorError as e:
                    pass
                except Exception as e:
                    logging.error(f"Error on attempt {attempt + 1}: {e}")

    return torrent_links

# Telegram bot command handler
async def start(update: Update, context: CallbackContext):
     update.message.reply_text('Hi! Send me a search query to find torrents.')

async def handle_message(update: Update, context: CallbackContext):
    query = update.message.text
    torrents =  search_torrent(query)

    if torrents:
        links = [torrent['link'] for torrent in torrents]
        torrent_links =  get_torrent1337x(links)

        response = ""
        for title, link, magnet in zip([t['title'] for t in torrents], links, torrent_links):
            response += f"Title: {title}\n"
            response += f"Link: {link}\n"
            response += f"Magnet: {magnet}\n\n"

        update.message.reply_text(response)
    else:
        update.message.reply_text("No torrents found.")


# Main function to run the bot
async def main():
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    # Add handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    # Start the Bot
    updater.start_polling()
    updater.idle()

# Run the async main function
if __name__ == "__main__":
    asyncio.run(main())
