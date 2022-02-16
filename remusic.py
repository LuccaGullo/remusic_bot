from discord.ext import commands, tasks
import discord
import yt_dlp
import asyncio
import os

from src.config import Config
config = Config().read()



TOKEN = config['TOKEN']

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
    'source_address': '0.0.0.0'
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = yt_dlp.YoutubeDL(ytdl_format_options)

client = commands.Bot(command_prefix='$')


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(
            executable="C:/Users/Geanluca/Downloads/ffmpeg-n4.4-latest-win64-gpl-4.4/bin/ffmpeg.exe",
            source=filename, **ffmpeg_options), data=data)


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


@client.event
async def on_ready():
    change_status.start()
    print('Bot is online!')


@client.command(name='ping', help='This command returns the latency.')
async def ping(ctx):
    await ctx.send(f'**Pong!**: {round(client.latency * 100)}ms')


@client.command(name='join', help='This command join a voice channel.')
async def join(ctx):
    if ctx.author.voice is None:
        await ctx.send("Não tem ninguém no canal de voz!")
    voice_channel = ctx.author.voice.channel
    if ctx.voice_client is None:
        await voice_channel.connect()
    else:
        await ctx.voice_client.move_to(voice_channel)


@client.command(name='leave', help='This command leave a voice channel.')
async def leave(ctx):
    await ctx.voice_client.disconnect()


@client.command(name='play', help='This command plays the song.')
async def play(ctx):
    url = (ctx.message.content.split('$play '))[1]
    if not ctx.message.author.voice:
        await ctx.send("You are not connected to a voice channel.")
        return

    else:
        channel = ctx.message.author.voice.channel

    if channel != None:
        try:
            await channel.connect()
        except:
            pass

    user_channel = ctx.author.voice.channel
    if user_channel:
        try:
            await ctx.voice_client.move_to(user_channel)
        except:
            pass

    server = ctx.message.guild
    voice_channel = server.voice_client

    async with ctx.typing():
        player = await YTDLSource.from_url(url, loop=client.loop)
        guild_id = ctx.message.guild.id

        if not queues:
            voice_channel.play(player, after=lambda x=None: check_queues(ctx, guild_id))
            await ctx.send('Now playing: **{}**!'.format(player.title))
        else:
            pass

        if guild_id in queues:
            queues[guild_id].append(player)
            await ctx.send(f"**{player.title}** has been added to the queue.")
        else:
            queues[guild_id] = [player]


@client.command(name='stop', help='This command stops the music and makes the bot leave the voice channel.')
async def stop(ctx):
    voice_client = ctx.message.guild.voice_client
    await voice_client.disconnect()


@client.command(name='resume', help='This command resumes the song.')
async def resume(ctx):
    voice_client = ctx.message.guild.voice_client
    await voice_client.resume()


@client.command(name='pause', help='This command pauses the song.')
async def pause(ctx):
    voice_client = ctx.message.guild.voice_client
    await voice_client.pause()


@client.command(name='skip', help='This command skips the actual song and plays the next one on the queue.')
async def skip(ctx):
    id = ctx.message.guild.id
    server1 = ctx.message.guild
    voice_client = ctx.message.guild.voice_client
    voice_client.pause()
    voice = server1.voice_client
    source = queues[id]
    filename = ytdl.prepare_filename(source[0].data)
    queues[id].pop(0)
    await ctx.send('Song Skipped!')

    if len(queues[789156365460832287]) > 0:
        voice.play(source[0], after=lambda x=None: check_queues(ctx, id))
        await ctx.send('Now playing: **{}**  '.format(source[0].title))
        os.remove(filename)
    else:
        queues.pop(789156365460832287)

    if queues == {}:
        await asyncio.sleep(300)
        await ctx.send("Bot disconnected because it's idle for a long time")
        await voice_client.disconnect()


@tasks.loop(seconds=20)
async def change_status():
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name='$help'))


client.run(TOKEN)

"""
1 - Make the queue/play accept playlists.   youtube-dl -i -f mp4 --yes-playlist 'https://www.youtube.com/watch?v=7Vy8970q0Xc&list=PLwJ2VKmefmxpUJEGB1ff6yUZ5Zd7Gegn2'

2 - Improve the search by writing. Maybe make the same way that the mp3 downloader. (5 options to the user pick 1.).  (Done)
Obs: The url search is working fine. 

3 - Erase the file after the song is over, maybe with 'os.remove(filename)'. ( 50% Done... The queue removes the file, but the skip doesn't.)

4 - if you call the bot to a 'x' channel and then switch channel and call him again, the bot doesn't join the new channel. (Done)

5 - Make bot disconnect after 10 minutes idle. (50% Done... The skip disconnects the bot, but the queue doesn't.)

6 - Make the bot 24hrs online without my pc.
"""