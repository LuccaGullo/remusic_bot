import yt_dlp
import os

queues = {}

yt_dlp.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
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

ytdl = yt_dlp.YoutubeDL(ytdl_format_options)


def check_queues(ctx, id):
    if queues[id] != []:
        server1 = ctx.message.guild
        voice = server1.voice_client
        id = ctx.message.guild.id
        source = queues[id]
        filename = ytdl.prepare_filename(source[0].data)
        queues[id].pop(0)

        if len(queues[789156365460832287]) > 0:
            voice.play(source[0], after=lambda x=None: check_queues(ctx, id))
            os.remove(filename)
        else:
            queues.pop(789156365460832287)