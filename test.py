import aiohttp
import asyncio
from bs4 import BeautifulSoup
import ssl
import logging

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

                    return results
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
        for link in links[:10]:
            for attempt in range(3):  # Retry up to 3 times
                try:
                    async with session.get(link, ssl=ssl_context) as req:
                        response_text = await req.text()
                        soup = BeautifulSoup(response_text, 'html.parser')
                        page_content = soup.find('div', class_="col-9 page-content")
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



# Example usage
async def main():
    query = 'The boys'
    torrents = await search_torrent(query)
    if torrents:
        links = [torrent['link'] for torrent in torrents]
        torrent_links = await get_torrent1337x(links)

        for title, link, magnet in zip([t['title'] for t in torrents], links, torrent_links):
            print(f"Title: {title}")
            print(f"Link: {link}")
            print(f"Magnet: {magnet}\n")
    else:
        print("No torrents found")

# Run the async main function
if __name__ == "__main__":
    asyncio.run(main())
