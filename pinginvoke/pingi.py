import contextlib
import json
import pathlib

from redbot.core import Config, commands

with open(pathlib.Path(__file__).parent / "info.json") as fp:
    __red_end_user_data_statement__ = json.load(fp)["end_user_data_statement"]


class PingInvoke(commands.Cog):
    """
    [botname]?

    Invoke the ping command by asking if your bot is there.
    """

    __author__ = "Kreusada"
    __version__ = "1.1.2"

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, 32482347932, force_registration=True)
        self.config.register_global(botname=None)
        if 719988449867989142 in self.bot.owner_ids:
            with contextlib.suppress(RuntimeError, ValueError):
                self.bot.add_dev_env_value(self.__class__.__name__.lower(), lambda x: self)

    def format_help_for_context(self, ctx: commands.Context) -> str:
        context = super().format_help_for_context(ctx)
        return f"{context}\n\nAuthor: {self.__author__}\nVersion: {self.__version__}"

    async def red_delete_data_for_user(self, **kwargs):
        """Nothing to delete"""
        return

    def cog_unload(self):
        if 719988449867989142 in self.bot.owner_ids:
            with contextlib.suppress(KeyError):
                self.bot.remove_dev_env_value(self.__class__.__name__.lower())

    @commands.group()
    @commands.is_owner()
    async def pingi(self, ctx: commands.Context):
        """Commands to configure PingInvoke."""

    @pingi.command(name="set")
    async def _set(self, ctx: commands.Context, botname: str):
        """
        Set the bot name to listen for.

        Example Input:
        `[p]pingi set wall-e`
        `[p]pingi set r2d2`
        `[p]pingi set [botname]`

        Usage:
        When you type [botname]?, or whatever you configure your name as,
        it will invoke the ping command.

        NOTE: Do not include the question mark.
        """
        await self.config.botname.set(botname)
        await ctx.send(
            f"{ctx.me.name} will now invoke the ping command when it hears `{botname}?`."
        )

    @pingi.command()
    async def reset(self, ctx):
        """Reset and disable PingInvoke."""
        await ctx.tick()
        await self.config.botname.clear()

    @pingi.command()
    async def settings(self, ctx):
        """Show the current settings for PingInvoke."""
        botname = await self.config.botname()
        if botname:
            await ctx.send(f"{ctx.me.name} will respond to `{botname}?`.")
        else:
            await ctx.send("A name has not been set.")

    @commands.Cog.listener()
    async def on_message_without_command(self, message):
        botname = await self.config.botname()
        if not botname:
            return
        if not message.guild:
            return
        if message.author.bot:
            return
        if await self.bot.cog_disabled_in_guild(self, message.guild):
            return
        if not await self.bot.ignored_channel_or_guild(message):
            return
        if not await self.bot.allowed_by_whitelist_blacklist(message.author):
            return
        if message.content.lower().startswith(botname.lower()) and message.content.endswith("?"):
            ctx = await self.bot.get_context(message)
            return await ctx.invoke(self.bot.get_command("ping"))
