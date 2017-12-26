'''
This entire file is by Ice, or IceeMC. We, as the cree-py organization, do NOT take any credit for this program. However, any bugs or fixes can be made by us and the MIT License for all work in this repository still applies.
'''

import asyncio
import discord
from discord.ext import commands


if not discord.opus.is_loaded():
    # the 'opus' library here is opus.dll on windows
    # or libopus.so on linux in the current directory
    # you should replace this with the location the
    # opus library is located in and with the proper filename.
    # note that on windows this DLL is automatically provided for you
    discord.opus.load_opus('opus')


class VoiceEntry:
    def __init__(self, message, player):
        self.requester = message.author
        self.channel = message.channel
        self.player = player

    def __str__(self):
        fmt = '**{0.title}** by **{0.uploader}**. As requested by **{1.display_name}** '
        duration = self.player.duration
        if duration:
            fmt = fmt + '({0[0]}:{0[1]})'.format(divmod(duration, 60))  # splits song duration into minutes and seconds
        return fmt.format(self.player, self.requester)  # 0s are replaced with the player, 1 is requester


class VoiceState:
    def __init__(self, bot, ctx):
        self.current = None
        self.voice = None
        self.bot = bot
        self.play_next_song = asyncio.Event()
        self.songs = asyncio.Queue()
        self.skip_votes = set()  # a set of user_ids that voted
        self.audio_player = self.bot.loop.create_task(self.audio_player_task(ctx))

    def is_playing(self):
        if self.voice is None or self.current is None:
            return False

        player = self.current.player
        return not player.is_done()  # what does this do lol

    @property
    def player(self):
        return self.current.player

    def skip(self):
        self.skip_votes.clear()  # clears all the votes to skip
        if self.is_playing():
            self.player.stop()  # stops the song

    def toggle_next(self):
        self.bot.loop.call_soon_threadsafe(self.play_next_song.set)

    async def audio_player_task(self, ctx):
        while True:
            self.play_next_song.clear()
            self.current = await self.songs.get()
            await ctx.send(self.current.channel, f'Now playing {self.current}')  # not sure how this will work, added ctx as an arg to the __init__
            self.current.player.start()
            await self.bot.change_presence(game=discord.Game(name='{0.title} by {0.uploader}'.format(self.player), type=2))
            await self.play_next_song.wait()


class Music:
    """Voice related commands.
    Works in multiple servers at once.
    """

    def __init__(self, bot):
        self.bot = bot
        self.voice_states = {}

    def get_voice_state(self, server):
        state = self.voice_states.get(server.id)
        if state is None:
            state = VoiceState(self.bot)
            self.voice_states[server.id] = state

        return state

    async def create_voice_client(self, channel):
        voice = await self.bot.join_voice_channel(channel)
        state = self.get_voice_state(channel.server)
        state.voice = voice

    def __unload(self):
        for state in self.voice_states.values():
            try:
                state.audio_player.cancel()
                if state.voice:
                    self.bot.loop.create_task(state.voice.disconnect())
            except:
                pass

    @commands.command(no_pm=True)
    async def join(self, ctx, *, channel: discord.VoiceChannel):
        """Joins a voice channel."""
        try:
            await self.create_voice_client(channel)
        except discord.ClientException:
            await ctx.send('Already in a voice channel...')
        except discord.InvalidArgument:
            await ctx.send('This is not a voice channel...')
        else:
            await ctx.send(f'Ready to play audio in **{channel.name}**')

    @commands.command(no_pm=True)
    async def summon(self, ctx):
        """Summons the bot to join your voice channel."""
        summoned_channel = ctx.author.voice_channel
        if summoned_channel is None:
            await ctx.send('Are you sure you\'re in a voice channel?')
            return False

        state = self.get_voice_state(ctx.guild)
        if state.voice is None:
            state.voice = await self.bot.join_voice_channel(summoned_channel)
        else:
            await state.voice.move_to(summoned_channel)

        return True

    @commands.command(no_pm=True)
    async def play(self, ctx, *, song: str):
        """Plays a song.
        If there is a song currently in the queue, then it is
        queued until the next song is done playing.
        This command automatically searches as well from YouTube.
        The list of supported sites can be found here:
        https://rg3.github.io/youtube-dl/supportedsites.html
        """
        state = self.get_voice_state(ctx.guild)
        opts = {
            'default_search': 'auto',
            'quiet': True,
        }

        if state.voice is None:
            success = await ctx.invoke(self.summon)
            await ctx.send("Loading the song, please be patient...")
            if not success:
                return

        try:
            player = await state.voice.create_ytdl_player(song, ytdl_options=opts, after=state.toggle_next)
        except Exception as e:
            fmt = f'An error occurred while processing this request: ```py\n{type(e).__name__}: {e}\n```'
            await ctx.send(fmt)
        else:
            player.volume = 0.6
            entry = VoiceEntry(ctx.message, player)
            await state.songs.put(entry)

    @commands.command(no_pm=True)
    async def volume(self, ctx, value: int):
        """Sets the volume of the currently playing song."""

        state = self.get_voice_state(ctx.guild)
        if state.is_playing():
            player = state.player
            player.volume = value / 100
            await ctx.send('Set the volume to {value}%')

    @commands.command(no_pm=True)
    async def resume(self, ctx):
        """Resumes the currently played song."""
        state = self.get_voice_state(ctx.guild)
        if state.is_playing():
            player = state.player
            player.resume()

    @commands.command(pass_context=True, no_pm=True)
    async def stop(self, ctx):
        """Stops playing audio and leaves the voice channel.
        This also clears the queue.
        """
        server = ctx.guild
        state = self.get_voice_state(server)

        if state.is_playing():
            player = state.player
            player.stop()

        try:
            state.audio_player.cancel()
            del self.voice_states[server.id]
            await state.voice.disconnect()
            await ctx.send("Cleared the queue and disconnected from voice channel ")
        except:
            pass

    @commands.command(no_pm=True)
    async def skip(self, ctx):
        """Vote to skip a song. The song requester can automatically skip.
        3 skip votes are needed for the song to be skipped.
        """

        state = self.get_voice_state(ctx.guild)
        if not state.is_playing():
            await ctx.send('Not playing any music right now...')
            return

        voter = ctx.author
        if voter == state.current.requester:
            await ctx.send('Requester requested skipping song...')
            state.skip()
        elif voter.id not in state.skip_votes:
            state.skip_votes.add(voter.id)
            total_votes = len(state.skip_votes)
            if total_votes >= 3:
                await ctx.send('Skip vote passed, skipping song...')
                state.skip()
            else:
                await ctx.send(f'Skip vote added, currently at [{total_votes}/3]')
        else:
            await ctx.send('You have already voted to skip this song.')

    @commands.command(no_pm=True)
    async def playing(self, ctx):
        """Shows info about the currently played song."""

        state = self.get_voice_state(ctx.guild)
        if state.current is None:
            await ctx.send('Not playing anything.')
        else:
            skip_count = len(state.skip_votes)
            await ctx.send(f'Now playing {state.current} [skips: {skip_count}/3]')


def setup(bot):
    bot.add_cog(Music(bot))
