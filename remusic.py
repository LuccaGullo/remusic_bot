# -*- coding: utf-8 -*-
import shutil

from discord.ext import commands, tasks
from src import ytdl_infos as yt
from src.config import Config
from src import get_url
import discord
import asyncio
import os


config = Config().read()
TOKEN = config['TOKEN']

queues = {}

client = commands.Bot(command_prefix=',')


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: yt.ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            data = data['entries'][0]

        filename = data['url'] if stream else yt.ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(
            executable="C:/Users/Geanluca/Downloads/ffmpeg-n4.4-latest-win64-gpl-4.4/bin/ffmpeg.exe",
            source=filename, **yt.ffmpeg_options), data=data)


def check_queues(ctx, id):
    if queues:
        server1 = ctx.message.guild
        voice = server1.voice_client
        id = ctx.message.guild.id
        source = queues[id]
        queues[id].pop(0)

        if len(queues[789156365460832287]) > 0:
            voice.play(source[0], after=lambda x=None: check_queues(ctx, id))
        else:
            queues.pop(789156365460832287)
            shutil.rmtree(yt.songs_path)


@client.event
async def on_ready():
    change_status.start()
    print('Remusic is online!')


@client.command(name='ping', help='This command returns the latency.')
async def ping(ctx):
    await ctx.send(f'**Pong!**: {round(client.latency * 100)}ms')


@client.command(name='join', help='This command join a voice channel.')
async def join(ctx):
    if ctx.author.voice is None:
        await ctx.send("You are not connected to a voice channel.")
    voice_channel = ctx.author.voice.channel
    if ctx.voice_client is None:
        await voice_channel.connect()
    else:
        await ctx.voice_client.move_to(voice_channel)


@client.command(name='leave', help='This command leave a voice channel.')
async def leave(ctx):
    await ctx.voice_client.disconnect()


@client.command(name='p', help='This command plays the song.')
async def p(ctx):
    search = (ctx.message.content.split(',p '))[1].encode("ascii","ignore").decode()

    if 'https://' in search:
        url_watch = search
        await ctx.channel.purge(limit=1)
    else:
        data = get_url.get_html_page(search.replace(' ', '+'))
        results = get_url.get_names_search(data)
        msg = ''
        for x in range(0, 5):
           msg += f"{(get_url.info_results(data))[x]} \n"
        await ctx.send(f'**Please select a track with the 1-5 numbers:** \n{msg}')

        def check(msg): return msg.author == ctx.author and msg.channel == ctx.channel

        choice = await client.wait_for("message", check=check)
        url_watch = get_url.get_url_watch((results[0][int(choice.content) - 1]))
        await ctx.channel.purge(limit=3)


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
        player = await YTDLSource.from_url(url_watch, loop=client.loop)
        guild_id = ctx.message.guild.id

        if not queues:
            voice_channel.play(player, after=lambda x=None: check_queues(ctx, guild_id))
            await ctx.send('Now playing: **{}**!'.format(player.title))

        if guild_id in queues:
            queues[guild_id].append(player)
            await ctx.send(f"**{str(ctx.message.author).split('#')[0]}** Added **{player.title}** to the queue.")
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


@client.command(name='s', help='This command skips the actual song and plays the next one on the queue.')
async def s(ctx):
    id = ctx.message.guild.id
    server1 = ctx.message.guild
    voice_client = ctx.message.guild.voice_client
    voice_client.pause()
    voice = server1.voice_client
    source = queues[id]
    queues[id].pop(0)
    await ctx.send('Song Skipped!')

    if len(queues[789156365460832287]) > 0:
        voice.play(source[0], after=lambda x=None: check_queues(ctx, id))
        await ctx.send('Now playing: **{}**  '.format(source[0].title))
    else:
        queues.pop(789156365460832287)


@tasks.loop(seconds=20)
async def change_status():
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=',help'))


client.run(TOKEN)

"""
1 - Make the queue/play accept playlists.  

2 - Make bot disconnect after 10 minutes idle.    
if queues == {}:
    await asyncio.sleep(300)
    await ctx.send("Bot disconnected because it's idle for a long time")
    await voice_client.disconnect()
"""