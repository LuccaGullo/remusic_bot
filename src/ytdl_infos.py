import yt_dlp

yt_dlp.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': 'C:/Users/Geanluca/PycharmProjects/remusic_bot/Songs/'
               '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
}

ffmpeg_options = {
    'options': '-vn'
}

songs_path = 'C:/Users/Geanluca/PycharmProjects/remusic_bot/Songs'

ytdl = yt_dlp.YoutubeDL(ytdl_format_options)
