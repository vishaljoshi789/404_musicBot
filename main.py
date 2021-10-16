import discord
from discord.ext import commands
from youtube_dl import YoutubeDL

BOT = commands.Bot(command_prefix='404')

class music_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.is_playing = False
        self.ctx = ''
        self.loop = False
        self.music_queue = []
        self.YDL_OPTIONS = {
          'format' : 'bestaudio/best',
          'postprocessors' : [{
            'key' : 'FFmpegExtractAudio',
            'preferredcodec' : 'mp3',
            'preferredquality' : '192',
          }], 'noplaylist':'True'}
        self.FFMPEG_OPTIONS = {'before_options':'-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options':'-vn'}

        self.vc = ''

    def search_yt(self, item):
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            try:
                info = ydl.extract_info(f'ytsearch:{item}', download=False)['entries'][0]
            except Exception:
                return False
            
        return {'source': info['formats'][0]['url'], 'title': info['title']}
