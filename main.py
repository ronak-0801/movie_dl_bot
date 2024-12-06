import asyncio
import logging
import ssl
from bs4 import BeautifulSoup
import aiohttp
from telegram import Update, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackContext
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get the bot token from environment variables
TOKEN = os.getenv('TOKEN')
# Configure logging
logging.basicConfig(level=logging.INFO)

# Function to search torrents asynchronously
async def search_torrent(query):
    url = f'https://www.1337x.to/search/{query}/1/'
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    async with aiohttp.ClientSession() as session:
        for attempt in range(3):  # Retry up to 3 times
            try:
                async with session.get(url, ssl=ssl_context) as response:
                    response_text = await response.text()
                    soup = BeautifulSoup(response_text, 'html.parser')
                    torrents = soup.find_all('a', href=True)
                    results = []

                    for torrent in torrents:
                        if 'torrent' in torrent['href']:
                            title = torrent.text.strip()
                            link = f"https://1337x.to{torrent['href']}"
                            results.append({'title': title, 'link': link})

                    return results  # Return only the first 5 results
            except aiohttp.ClientConnectorError as e:
                pass
                # logging.error(f"Connection error on attempt {attempt + 1}: {e}")
            except Exception as e:
                logging.error(f"Error on attempt {attempt + 1}: {e}")

    return []

# Function to get magnet link asynchronously
async def get_torrent1337x(links):
    torrent_links = []
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    async with aiohttp.ClientSession() as session:
        for link in links[:3]:  # Limit to the first 5 links
            for attempt in range(3):  # Retry up to 3 times
                try:
                    async with session.get(link['link'], ssl=ssl_context) as req:
                        response_text = await req.text()
                        soup = BeautifulSoup(response_text, 'html.parser')
                        page_content = soup.find('div', class_="col-9 page-content")

                        # Check if it's a movie or series link
                        if page_content and ('Movies' in page_content.text or 'TV' in page_content.text):
                            magnet_link_tag = page_content.find('li').find('a', href=True)

                            if magnet_link_tag and 'magnet:' in magnet_link_tag['href']:
                                torrent_links.append(magnet_link_tag['href'])
                            else:
                                torrent_links.append(None)
                        break
                except aiohttp.ClientConnectorError as e:
                    # logging.error(f"Connection error on attempt {attempt + 1}: {e}")
                    pass
                except Exception as e:
                    logging.error(f"Error on attempt {attempt + 1}: {e}")

    return torrent_links

# Initialize your bot token

# Define a function to handle the /search command
def search(update: Update, context: CallbackContext) -> None:
    query = ' '.join(context.args)
    asyncio.run(handle_search(update, query))

# Async function to handle search and response
async def handle_search(update: Update, query: str) -> None:
    torrents = await search_torrent(query)

    if torrents:
        torrent_links = await get_torrent1337x(torrents)

        # Prepare the message
        message = ""
        for idx, (torrent, magnet) in enumerate(zip(torrents, torrent_links), start=1):
            message += f"{idx}. Title: {torrent['title']}\n"
            if magnet:
                message += f"   Magnet: {magnet}\n\n"
            else:
                message += "   No magnet link available\n\n"
            if idx >= 5:  # Limit to the first 5 torrents
                break

        if len(torrents) > 5:
            message += "...\n\n"
            message += "There are more results. Use /next for more."

        update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
    else:
        update.message.reply_text("No torrents found for your query.")

# Create an updater and pass your bot's token
updater = Updater(token=TOKEN, use_context=True)

# Get the dispatcher to register handlers
dispatcher = updater.dispatcher

# Register the /search command handler
dispatcher.add_handler(CommandHandler("search", search))

# Start the Bot
updater.start_polling()
updater.idle()
