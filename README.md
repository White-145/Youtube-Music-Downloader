## Outdated

This project is very old, I can't guarantee it works and am not interested in updating. If you want to download music from youtube, you can use python modules `yt-dlp`, `eyed3` and `azapi` with this script (windows):

```batch
@echo off

set argC=0
for %%x in (%*) do Set /A argC+=1
rem allow only 1 argument
if %argC% == 1 (
	cmd /V /C echo(!%*!| findstr /I "music." > nul && (
		rem music

		cmd /V /C echo(!%*!| findstr /I "v=" > nul && (
			rem single
			yt-dlp %* --no-warnings --restrict-filename --no-playlist -x --audio-format mp3 --audio-quality 0 --add-metadata --embed-thumbnail --convert-thumbnail jpg --ppa "EmbedThumbnail+ffmpeg_o:-c:v mjpeg -vf crop=\"'if(gt(ih,iw^),iw,ih^)':'if(gt(iw,ih^),ih,iw^)'\"" -o "%UserProfile%/Desktop/ymd_result/music/%%(channel)s_-_%%(track)s_%%(id)s.%%(ext)s" --exec lyrics.py
			EXIT /b
		) || (
			rem full playlist
			yt-dlp %* --no-warnings --restrict-filename -x --audio-format mp3 --audio-quality 0 --add-metadata --embed-thumbnail --convert-thumbnail jpg --ppa "EmbedThumbnail+ffmpeg_o:-c:v mjpeg -vf crop=\"'if(gt(ih,iw^),iw,ih^)':'if(gt(iw,ih^),ih,iw^)'\"" -o "%UserProfile%/Desktop/ymd_result/music/%%(album)s/%%(channel)s_-_%%(track)s_%%(id)s.%%(ext)s" --exec lyrics.py
			EXIT /b
		)
	) || (
		rem video
		yt-dlp %* --no-warnings --restrict-filenames -f "bestvideo[height<=720]+bestaudio/best[height<=720]" -o "%UserProfile%/Desktop/ymd_result/%%(title)s.%%(ext)s" --recode-video mp4
		EXIT /b
	)
)
```

`lyrics.py`:

```python
from sys import argv
from azapi import AZlyrics
from eyed3 import load
from eyed3.id3 import ID3_V1, Genre
from os.path import basename
from youtube_dl import YoutubeDL
from re import match

API = AZlyrics('google', accuracy=0.5)

tag = load(argv[1]).tag

API.artist = tag.artist
API.title = tag.title

lyrics = API.getLyrics()

video_id = match('.*_-_.*([a-zA-Z0-9_-]{11})\\.mp3$', basename(argv[1])).group(1)
print(video_id)

with YoutubeDL() as ydl:
	info_dict = ydl.extract_info(video_id, download=False)
	video_description = info_dict.get("description", None)

tag.comments.set(
	'Downloaded using yt-dlp\nhttps://www.youtube.com/watch?v=' + video_id
	+ ('\n\n' + video_description if video_description is not None else "")
)
if isinstance(lyrics, str): tag.lyrics.set(lyrics, "AZlyrics")
tag.save()

# fix yt-dlp's "www.youtube.com/watch?v=" comment
tag_v1 = load(argv[1], ID3_V1).tag
tag_v1.comments[0].text = video_id
tag_v1.save()
```

## What is Youtube Music Downloader

This is a python program that allows you to download music from Youtube Music with all metadata (from youtube music)

## How to install

To use you need to install 3 custom modules:
* ytmusicapi (for searching and metadata)
* youtube_dl (for downloading)
* eyeD3 (for editing metadata)

using
> pip install ytmusicapi

> pip install youtube_dl

> pip install eyed3

After that you can use this program
