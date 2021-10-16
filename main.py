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
    
    def play_next(self):
        if len(self.music_queue)>0:
            self.is_playing = True

            m_url = self.music_queue[0][0]['source']
            self.music_queue.pop(0)


            self.ctx.voice_client.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after = lambda e : self.play_next())

            
        else:
            self.is_playing = False

    async def play_music(self):
        if len(self.music_queue)>0:
            self.is_playing = True

            m_url = self.music_queue[0][0]['source']

            if self.vc == '':
              self.vc = await self.music_queue[0][1].connect()
            elif self.music_queue[0][1] != self.vc:
              self.vc.disconnect()
              self.vc = await self.music_queue[0][1].connect()
              
            await self.ctx.send('Now playing : ' + self.music_queue[0][0]['title'])

            try:
              self.ctx.voice_client.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after = lambda e : self.play_next())
            except:
              await self.ctx.send(self.vc)
            try:
              self.music_queue.pop(0)
            except:
              await self.ctx.send(self.music_queue)

        else:
            self.is_playing = False

    @commands.command(name='play', aliases=['p'], help='Plays a song.')
    async def play(self, ctx, *args):
        query = " ".join(args)
        if ctx.author.voice:
          voice_channel = ctx.author.voice.channel
          self.ctx = ctx
          if voice_channel is None:
              await ctx.send('Connect to a voice channel!')
          else:
              song = self.search_yt(query)
              if type(song) == type(True):
                  await ctx.send('Could not download the song. Incorrect format try another keyword. This could be due to playlist or a livestream')
              else:
                  self.music_queue.append([song, voice_channel])
                  if self.is_playing == False:
                      await self.play_music()
                  else:
                      await ctx.send(self.music_queue[len(self.music_queue)-1][0]['title']+' added to the queue')
        else:
          await ctx.send('Connect to a voice channel!')

                    

    @commands.command(name='queue', aliases=['q'], help='List the queue songs')
    async def queue(self, ctx):
        retval = ''
        for i in range(0, len(self.music_queue)):
            retval += self.music_queue[i][0]['title'] + '\n'

        print(retval)
        if retval != '':
            await ctx.send(retval)
        else:
            await ctx.send('No music in queue')

    @commands.command(name='skip', aliases=['sk'],help='Skip the current song')
    async def skip(self, ctx):
        if self.vc != '':
              ctx.voice_client.stop()
              await ctx.send('after using skip'+ str(self.music_queue))
              await self.play_music()


    @commands.command(name='stop', aliases=['st'], help='Stop the song and clear queue songs')
    async def stop(self, ctx):
      if self.vc != '':
        ctx.voice_client.stop()
        await ctx.send('Stoped')
        self.music_queue = []

    @commands.command(name='pause', aliases=['pp'], help='Pause the current song')
    async def pause(self, ctx):
      if self.vc != '':
        self.vc.pause()
        await ctx.send('Paused')

    @commands.command(name='resume', aliases=['re'], help='Resume the paused song')
    async def resume(self, ctx):
      if self.vc != '':
        self.vc.resume()
        await ctx.send('Resumed')

    @commands.command(name='disconnect', aliases=['dc'], help='Disconnect')
    async def disconnect(self, ctx):
      if self.vc != '':
        self.music_queue = []
        self.vc = ''
        await ctx.voice_client.disconnect()
        await ctx.send('Disconnected')

    @commands.command(name='completemysentence', aliases=['cms'])
    async def completemysentence(self, ctx, name):
      if name in ['vipul', 'Vipul']:
        await ctx.send('Chutea he sala!')

      elif name in ['himanshu', 'Himanshu']:
        await ctx.send('MOTA he sala!')


    # @commands.command(name='loop', aliases=['loo'], help='Loop the current song')
    # async def loop(self, ctx):
    #   if self.loop == False:
    #     self.loop = True
      


    
    


BOT.add_cog(music_cog(BOT))

with open('token.txt') as file:
    token = file.read()

keep_alive()

BOT.run(token)
