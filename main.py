import os
from urllib.request import urlretrieve

import eyed3
import youtube_dl
from ytmusicapi import YTMusic

import colors
import key_handler

class Downloader:
	# Download best and convert to mp3
	ydl_opts = {
		'format': 'bestaudio/best',
		'postprocessors': [{
			'key': 'FFmpegExtractAudio',
			'preferredcodec': 'mp3',
			'preferredquality': '192',
		}],
	}
	# Colors
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
	
	@staticmethod
	def show_item(category, index):
		index += 1
		print("\x1b[s", end='')  # Save cursor position
		print("\x1b[J", end='')  # Clear screen
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
		print("\x1b[u", end='')  # Restore cursor position
	
	def from_link(self, link):
		if link.startswith("https://"):
			link = link[26:]
		else:
			link = link[18:]

		if link.startswith("watch?v="):
			self.type = "song"
			self.video_id = link[8:].split('&')[0]
			return True

		return False
	
	@staticmethod
	def return_search(error='', after_result=False):
		print("\x1b[u", end='')       # Restore cursor
		if after_result:
			print("\x1b[2F", end='')  # Move 2 lines up
		print("\x1b[1F", end='')      # Move 1 line up
		print("\x1b[J", end='')       # Clear screen
		print(Downloader.color_tip.text(error))
	
	def search(self):
		while True:
			print("\x1b[s", end='')     # Save cursor
			print("\x1b[J", end='')     # Clear screen
			print("\x1b[?25h", end='')  # Show cursor
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
			
			result_song_raw = Downloader.ytmusic.search(query=query, filter="songs", limit=40)
			result_album_raw = Downloader.ytmusic.search(query=query, filter="albums", limit=40)

			del query

			# Convert songs and albums to dict
			result_song = ["song"]
			result_album = ["album"]
			for song in result_song_raw:
				result_song.append({
					'type': "song",
					'title': song['title'],
					'author': song['artists'][0]['name'],
					'album': song['album']['name'],
					'id': song['videoId']
				})
			for album in result_album_raw:
				result_album.append({
					'type': "album",
					'title':  album['title'],
					'author': album['artists'][0]['name'],
					'id': album['browseId']
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

			print("\x1b[?25l", end='')  # Hide cursor
			Downloader.show_item(categories[0], 0)
			
			while (key := key_handler.wait_key()) != key_handler.Key.ESC:
				match key:
					case key_handler.Key.ENTER:
						break
					
					case key_handler.Key.UP:
						category = (category + 1) % len(categories)
						index = 0

					case key_handler.Key.DOWN:
						category = (category - 1) % len(categories)
						index = 0
					
					case key_handler.Key.LEFT:
						index = (index - 1) % (len(categories[category]) - 1)
					
					case key_handler.Key.RIGHT:
						index = (index + 1) % (len(categories[category]) - 1)
					
				Downloader.show_item(categories[category], index)

			else:
				Downloader.return_search(after_result=True)
				continue

			print("\x1b[?25h", end='')  # Show cursor
			selected = categories[category][index + 1]
			del categories, category, index
			
			self.type = selected['type']
			if self.type == "song":
				self.video_id = selected['id']
			else:
				self.playlist_id = selected['id']
			
			print(colors.GREY)
			print("\x1b[1F", end='')             # Move 1 line up
			print("\x1b[J", end='', flush=True)  # Clear screen
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
		print(colors.END + "\x1b[?25h", end='')  # Remove colors and show cursor

