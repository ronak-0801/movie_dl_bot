# import asyncio
# import libtorrent as lt

# # Function to download torrent using magnet link
# async def download_torrent(magnet_link, save_path='./downloads/'):
#     ses = lt.session()
#     params = {
#         'save_path': save_path,
#         'storage_mode': lt.storage_mode_t(2),
#         'paused': False,
#         'auto_managed': True,
#         'duplicate_is_error': True
#     }
#     handle = lt.add_magnet_uri(ses, magnet_link, params)
#     print(f"Downloading: {handle.name()}")

#     while not handle.is_seed():
#         s = handle.status()
#         print(f"Downloading {s.download_rate / 1000} kB/s, uploading {s.upload_rate / 1000} kB/s, peers: {s.num_peers}")
#         await asyncio.sleep(1)

#     print("Download complete!")
#     ses.remove_torrent(handle)

# # Example usage in main function
# async def main():
#     magnet_link = 'magnet:?xt=urn:btih:1C6B2179BCD73EFD07FB8018268598C062CF95AF&dn=Inception.2010.1080p.BluRay.DDP5.1.x265.10bit-GalaxyRG265'
#     await download_torrent(magnet_link)

# # Run the async main function
# if __name__ == "__main__":
#     asyncio.run(main())
