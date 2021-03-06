import urllib.request
import os

from ytmusicapi import YTMusic
import youtube_dl
import eyed3

def get_os_name(name):
    os_name = name.replace('/', '')
    os_name = os_name.replace('\\', '')
    os_name = os_name.replace(':', '')
    os_name = os_name.replace('*', '')
    os_name = os_name.replace('?', '')
    os_name = os_name.replace('"', "'")
    os_name = os_name.replace('<', '')
    os_name = os_name.replace('>', '')
    os_name = os_name.replace('|', '')

    return os_name

if not os.path.exists("tmp"):
    os.mkdir("tmp")

if not os.path.exists("out"):
    os.mkdir("out")

ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}

os.chdir('tmp')

class Downloader:
    def __init__(self):
        self.video_id = None
        self.lyrics = None
        self.url = None
        self.name = None
        self.os_name = None
        self.author = None
        self.year = None
        self.album = None
        self.true_name = None

    def search(self):
        end = False
        while True:
            query = input("Search query or youtube music link: ")
            print()
            if query == '':
                continue

            if query.startswith("https://music.youtube.com/watch?v=") or query.startswith("music.youtube.com/watch?v="):
                self.video_id = query[34:-1].split('&')[0]
                break

            search_results = ytmusic.search(query=query, filter="songs", limit=5)

            if len(search_results) == 0:
                print("Nothing found, please try again")
                print()
                continue
            
            length = max([len(x['title']) for x in search_results][:5])
            tracks = 5 if len(search_results) > 5 else len(search_results)
            
            for i in range(tracks):
                print(f"{{{i + 1}}} {search_results[i]['title']}{' ' * (length - len(search_results[i]['title']))} - {search_results[i]['artists'][0]['name']}")
            
            while True:
                try:
                    print()
                    select = int(input(f'Select one of the tracks or 0 to return: '))
                except ValueError:
                    continue
                else:
                    if select in range(1, tracks):
                        self.video_id = search_results[select - 1]['videoId']
                        end = True
                        break
                    if select == 0:
                        print()
                        break
            if end:
                break

    def get_metadata(self):
        print()
        print("[ymd] getting song metadata")

        metadata = ytmusic.get_song(videoId=self.video_id)

        playlist = ytmusic.get_watch_playlist(videoId=self.video_id)
        browse_id = playlist['lyrics']
        try:
            self.lyrics = ytmusic.get_lyrics(browseId=browse_id)['lyrics']
        except Exception:
            self.lyrics = ''

        self.url = metadata['microformat']['microformatDataRenderer']['urlCanonical']
        urllib.request.urlretrieve(metadata['videoDetails']['thumbnail']['thumbnails'][-1]['url'], f'thumbnail-{self.video_id}.png')

        self.name = metadata['videoDetails']['title']
        self.author = metadata['videoDetails']['author']
        self.year = int(metadata['microformat']['microformatDataRenderer']['uploadDate'].split('-')[0])
        self.album = playlist['tracks'][0]['album']['name']

        self.os_name = get_os_name(metadata['microformat']['microformatDataRenderer']['title'][:-16])
        self.true_name = f'{self.os_name}-{self.video_id}'
        self.true_name_2 = f'{get_os_name(self.name)}-{self.video_id}'

    def download(self):
        if os.path.exists(f'../out/{self.os_name}.mp3'):
            os.remove(f'../out/{self.os_name}.mp3')

        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.url])
        except Exception:
            print("[ymd] download failed")
            return False

        return True

        os.rename(f'{self.true_name}.mp3', f'{self.os_name}.mp3')

    def edit_metadata(self):
        print("[ymd] editing file metadata")
        while True:
            try:
                audiofile = eyed3.load(f'{self.os_name}.mp3')
            except OSError:
                if os.path.exists(f'{self.true_name}.mp3'):
                    os.rename(f'{self.true_name}.mp3', f'{self.os_name}.mp3')
                elif os.path.exists(f'{self.true_name_2}.mp3'):
                    os.rename(f'{self.true_name_2}.mp3', f'{self.os_name}.mp3')
                else:
                    print("[ymd] something went wrong...")
                    return False
            else:
                break
        audiofile.initTag()

        audiofile.tag.artist = self.author
        audiofile.tag.album = self.album
        audiofile.tag.title = self.name
        audiofile.tag.recording_date = self.year
        audiofile.tag.lyrics.set(self.lyrics)
        audiofile.tag.images.set(3, open(f'thumbnail-{self.video_id}.png', 'rb').read(), 'image/png')

        audiofile.tag.save()

    def end(self):
        print("[ymd] deleting temp files")

        os.remove(f'thumbnail-{self.video_id}.png')
        print()
        if os.path.exists(f'{self.os_name}.mp3'):
            os.rename(f'{self.os_name}.mp3', f'../out/{self.os_name}.mp3')

            print(f'Saved to /out/{self.os_name}.mp3')
            print()


        self.video_id = None
        self.lyrics = None
        self.url = None
        self.name = None
        self.os_name = None
        self.author = None
        self.year = None
        self.album = None

    def main(self):
        self.search()
        self.get_metadata()
        if self.download():
            self.edit_metadata()
        self.end()

ytmusic = YTMusic()
downloader = Downloader()

while True:
    downloader.main()