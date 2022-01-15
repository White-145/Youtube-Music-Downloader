import urllib.request
import os

from ytmusicapi import YTMusic
import youtube_dl
import eyed3

# set up folders
if not os.path.exists("tmp"):
    os.mkdir("tmp")

if not os.path.exists("out"):
    os.mkdir("out")

# variables
ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}
ytmusic = YTMusic()

default = "LSD - Genius"

# change directory to tmp/
os.chdir('tmp')

# main loop
try:
    while True:
        # search
        while True:
            query = input("Search query or youtube music link: ")

            # if empty
            if query == '':
                print()
                print(f'Using "{default}" as search query...')
                query = default

            # if link
            if query.startswith("https://music.youtube.com/watch?v="):
                video_id = query[34:-1].split('&')[0]
                break

            search_results = ytmusic.search(query=query, filter="songs", limit=10)

            # if nothing found
            print()
            if len(search_results) == 0:
                print("Nothing found, please try again")
                print()
                continue
            for i in range(len(search_results)):
                print(f"{{{i + 1}}}", search_results[i]["title"])

            while True:
                print()
                try:
                    selection = int(input(f'Select one of the tracks found when searching "{query}" using numbers 1-{len(search_results)}, or write 0 to return to the search: '))
                except ValueError:
                    continue
                else:
                    if selection in range(len(search_results) + 1):
                        song = search_results[selection - 1]
                        video_id = song['videoId']
                        break

            if selection != 0:
                break

        metadata = ytmusic.get_song(videoId=video_id)
        watch_playlist = ytmusic.get_watch_playlist(videoId=video_id)
        browse_id = watch_playlist['lyrics']
        try:
            lyrics = ytmusic.get_lyrics(browseId=browse_id)
        except Exception:
            lyrics = {'lyrics': ''}
        url = metadata['microformat']['microformatDataRenderer']['urlCanonical']

        # get metadata
        urllib.request.urlretrieve(metadata['videoDetails']['thumbnail']['thumbnails'][-1]['url'], f'thumbnail-{video_id}.png')
        name = metadata['videoDetails']['title']
        author = metadata['videoDetails']['author']
        year = int(metadata['microformat']['microformatDataRenderer']['uploadDate'].split('-')[0])
        album = watch_playlist['tracks'][0]['album']['name']
        lyrics_text = lyrics['lyrics']

        # full name without forbidden symbols: /\:*?"<>|
        os_name = metadata['microformat']['microformatDataRenderer']['title'][:-16]
        os_name = os_name.replace('/', '')
        os_name = os_name.replace('\\', '')
        os_name = os_name.replace(':', '')
        os_name = os_name.replace('*', '')
        os_name = os_name.replace('?', '')
        os_name = os_name.replace('"', "'")
        os_name = os_name.replace('<', '')
        os_name = os_name.replace('>', '')
        os_name = os_name.replace('|', '')

        print()

        # download song
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        try:
            os.remove(f'../out/{os_name}.mp3')
        except FileNotFoundError:
            pass

        # edit metadata
        os.rename(f'{os_name}-{video_id}.mp3', f'{os_name}.mp3')
        while True:
            try:
                audiofile = eyed3.load(f'{os_name}.mp3')
            except FileNotFoundError:
                os.rename(f'{os_name}-{video_id}.mp3', f'{os_name}.mp3')
                continue
            else:
                break
        audiofile.initTag()

        audiofile.tag.artist = author
        audiofile.tag.album = album
        audiofile.tag.title = name
        audiofile.tag.recording_date = year
        audiofile.tag.lyrics.set(lyrics_text)
        audiofile.tag.images.set(3, open(f'thumbnail-{video_id}.png', 'rb').read(), 'image/png')

        audiofile.tag.save()

        # remove temp files and move song to out/ folder
        os.remove(f'thumbnail-{video_id}.png')
        os.rename(f'{os_name}.mp3', f'../out/{os_name}.mp3')

        print()
        print(f'Saved to out/{os_name}.mp3')
        print()
except KeyboardInterrupt:
    pass