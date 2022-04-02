import os
import sys
from urllib.request import urlretrieve

import eyed3
import youtube_dl
from ytmusicapi import YTMusic

import colors
import key_handler


def wrap(num, min, max):
	if min > max:
		min, max = max, min
	return (num - min) % (max - min + 1) + min

def save_cursor():
	print("\x1b[s", end='', flush=True)

def restore_cursor():
	print("\x1b[u", end='', flush=True)

def clear():
	print("\x1b[J", end='', flush=True)

def move_y(step):
	print(f'\x1b[{step}F', end='', flush=True)

def hide():
	print("\x1b[?25l", end='', flush=True)

def show():
	print("\x1b[?25h", end='', flush=True)

def show_item(category, index):
	index += 1
	save_cursor()
	clear()
	print(Downloader.color_top.text(f'{category[0].title()} #{index}'))
	print(f'{Downloader.color_key.text("Name:")}   {category[index]["title"]}')
	print(f'{Downloader.color_key.text("Author:")} {category[index]["author"]}')
	if category[0] == "song":
		print(f'{Downloader.color_key.text("Album:")}  {category[index]["album"]}')
	elif category[0] == "playlist":
		print(f'{Downloader.color_key.text("Items:")}  {category[index]["items"]}')
	
	print()
	print("Enter to select")
	print("Esc to back")
	restore_cursor()

class Downloader:
	ydl_opts = {
		'format': 'bestaudio/best',
		'postprocessors': [{
			'key': 'FFmpegExtractAudio',
			'preferredcodec': 'mp3',
			'preferredquality': '192',
		}],
	}
	color_top = colors.Color(attr=colors.BOLD)
	color_key = colors.Color(colors.BEIGE)
	color_tip = colors.Color(colors.GREY)

	ytmusic = YTMusic()

	def __init__(self):
		self.type = None
		self.playlist_id = None
		self.video_id = None

		self.title = None
		self.author = None
		self.album = None

		self.os_name = None
		self.true_name = None

		self.year = None
		self.lyrics = None

		self.url = None

	@staticmethod
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
	
	def from_link(self, link):
		if link.startswith("https://"):
			link = link[26:]
		else:
			link = link[18:]

		if link.startswith("watch?v="):
			self.type = "song"
			self.video_id = link[8:].split('&')[0]
			return True

		if link.startswith("playlist?list="):
			self.type = "playlist"
			self.playlist_id = link[14:]
			return True

		return False
	
	@staticmethod
	def return_search(error='', after_result=False):
		restore_cursor()
		if after_result:
			move_y(2)
		move_y(1)
		clear()
		print(Downloader.color_tip.text(error))
	
	def search(self):
		while True:
			save_cursor()
			clear()
			show()
			query = input("Search query or link: ")
			print()
			if query == '':
				Downloader.return_search("Query shouldn't be empty")
				continue

			if query.startswith("https://") or query.startswith("music.youtube.com/"):
				if self.from_link(query):
					del query
					break
				else:
					Downloader.return_search("Wrong link")
					continue
			
			result_song_raw = Downloader.ytmusic.search(query=query, filter="songs")[:20]
			result_album_raw = Downloader.ytmusic.search(query=query, filter="albums")[:20]

			del query

			result_song = ["song"]
			result_album = ["album"]
			for i in range(len(result_song_raw)):
				result_song.append({
					'type': "song",
					'title': result_song_raw[i]['title'],
					'author': result_song_raw[i]['artists'][0]['name'],
					'album': result_song_raw[i]['album']['name'],
					'id': result_song_raw[i]['videoId']
				})
			for i in range(len(result_album_raw)):
				result_album.append({
					'type': "album",
					'title':  result_album_raw[i]['title'],
					'author': result_album_raw[i]['artists'][0]['name'],
					'id': result_album_raw[i]['browseId']
				})
			
			del result_song_raw, result_album_raw

			category = 0
			index = 0
			categories = []
			if len(result_song) > 1:
				categories.append(result_song)
			if len(result_album) > 1:
				categories.append(result_album)

			if len(categories) == 0:
				Downloader.return_search("No results")
				continue

			hide()
			show_item(categories[0], 0)
			
			while (key := key_handler.wait_key()) != key_handler.Key.ESC:
				match key:
					case key_handler.Key.ENTER:
						break
					
					case key_handler.Key.UP:
						category = wrap(category + 1, 0, len(categories) - 1)
						index = 0

					case key_handler.Key.DOWN:
						category = wrap(category - 1, 0, len(categories) - 1)
						index = 0
					
					case key_handler.Key.LEFT:
						index = wrap(index - 1, 0, len(categories[category]) - 2)
					
					case key_handler.Key.RIGHT:
						index = wrap(index + 1, 0, len(categories[category]) - 2)
					
				show_item(categories[category], index)

			else:
				Downloader.return_search(after_result=True)
				continue

			show()
			selected = categories[category][index + 1]
			del categories, category, index
			
			self.type = selected['type']
			if self.type == "song":
				self.video_id = selected['id']
			else:
				self.playlist_id = selected['id']
			
			print(colors.GREY)
			move_y(1)
			clear()
			break
	
	def catch_metadata(self, album=None):
		song = Downloader.ytmusic.get_song(self.video_id)

		playlist = Downloader.ytmusic.get_watch_playlist(videoId=self.video_id)
		browse_id = playlist['lyrics']
		try:
			self.lyrics = Downloader.ytmusic.get_lyrics(browseId=browse_id)['lyrics']
		except Exception:
			self.lyrics = ''
		if self.lyrics is None:
			self.lyrics = ''

		urlretrieve(song['videoDetails']['thumbnail']['thumbnails'][-1]['url'], f'thumbnail-{self.video_id}.png')

		self.title = song['videoDetails']['title']
		self.author = song['videoDetails']['author']
		self.year = int(song['microformat']['microformatDataRenderer']['uploadDate'].split('-')[0])
		if album is not None:
			self.album = album
		else:
			self.album = playlist['tracks'][0]['album']['name']

		self.os_name = Downloader.get_os_name(song['microformat']['microformatDataRenderer']['title'][:-16])
		self.true_name = f'{self.os_name}-{self.video_id}'

		self.url = song['microformat']['microformatDataRenderer']['urlCanonical']

	def download(self):
		if os.path.exists(f'../out/{self.os_name}.mp3'):
			os.remove(f'../out/{self.os_name}.mp3')

		try:
			with youtube_dl.YoutubeDL(Downloader.ydl_opts) as ydl:
				ydl.download([self.url])
		except Exception:
			return

		if not os.path.exists(f'{self.os_name}.mp3'):
			os.rename(f'{self.true_name}.mp3', f'{self.os_name}.mp3')

	def edit_metadata(self):
		while True:
			try:
				file = eyed3.load(f'{self.os_name}.mp3')
			except OSError:
				if os.path.exists(f'{self.true_name}.mp3'):
					os.rename(f'{self.true_name}.mp3', f'{self.os_name}.mp3')
				else:
					return
			else:
				break

		file.initTag()

		file.tag.artist = self.author
		file.tag.album = self.album
		file.tag.title = self.title
		file.tag.recording_date = self.year
		file.tag.lyrics.set(self.lyrics)
		file.tag.images.set(3, open(f'thumbnail-{self.video_id}.png', 'rb').read(), 'image/png')

		file.tag.save()

	def end(self):
		if os.path.exists(f'thumbnail-{self.video_id}.png'):
			os.remove(f'thumbnail-{self.video_id}.png')

		if os.path.exists(f'{self.os_name}.mp3'):
			os.rename(f'{self.os_name}.mp3', f'../out/{self.os_name}.mp3')

			Downloader.return_search(f'Saved to /out/{self.os_name}.mp3', True)

		self.type = None
		self.playlist_id = None
		self.video_id = None
		self.title = None
		self.author = None
		self.album = None
		self.os_name = None
		self.true_name = None
		self.year = None
		self.lyrics = None
		self.url = None


def main():
	if not os.path.exists("tmp"):
		os.mkdir("tmp")
	if not os.path.exists("out"):
		os.mkdir("out")

	os.chdir('tmp')

	print()

	while True:

		downloader = Downloader()

		downloader.search()
		if downloader.type == "song":
			downloader.catch_metadata()
			downloader.download()
			downloader.edit_metadata()
			downloader.end()
			continue

		album = Downloader.ytmusic.get_album(downloader.playlist_id)
		name = album['title']
		Downloader.return_search()
		for track in range(len(album['tracks'])):
			print(f'{colors.GREY}Downloading {track + 1}/{len(album["tracks"])}')

			downloader.video_id = album['tracks'][track]['videoId']

			downloader.catch_metadata(name)
			downloader.download()
			downloader.edit_metadata()
			downloader.end()

if __name__ == '__main__':
	try:
		main()
	finally:
		print(colors.END)
		show()

