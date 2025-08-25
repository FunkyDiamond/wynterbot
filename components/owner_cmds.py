import asyncio
from twitchio.ext import commands

# Owner Commands, only usable by you. Usefull for reloading commands without restarting the whole bot as well as testing commands.

# Custom Exception for our component guard.
class NotOwnerError(commands.GuardFailure): ...

class OwnerCmds(commands.Component):


    def __init__(self, bot: commands.Bot) -> None:
        # Passing args is not required...
        # We pass bot here as an example...
        self.bot = bot

    async def component_command_error(self, payload: commands.CommandErrorPayload) -> bool | None:
        error = payload.exception
        if isinstance(error, NotOwnerError):
            ctx = payload.context

            await ctx.reply("Only the owner can use this command!")

            # This explicit False return stops the error from being dispatched anywhere else...
            return False
        
    # Restrict all of the commands in this component to the owner.
    @commands.Component.guard()
    def is_owner(self, ctx: commands.Context) -> bool:
        if ctx.chatter.id == USER_ID:
            return True
        else:
            raise NotOwnerError
    
    # Manually load the cmds module.
    @commands.command()
    async def load(self, ctx: commands.Context) -> None:
        await self.bot.load_module("components.cmds")
        await self.bot.load_module("components.chat")
        await self.bot.load_module("components.redeems")
        await self.bot.load_module("components.owner_cmds")
        await self.bot.load_module("components.listeners")

    # Manually unload the cmds module.
    @commands.command()
    async def unload(self, ctx: commands.Context) -> None:
        await self.bot.unload_module("components.cmds")

    # Hot reload the cmds module automically.
    @commands.command()
    async def reload(self, ctx: commands.Context) -> None:
        await self.bot.reload_module("components.cmds")
        await self.bot.reload_module("components.chat")
        await self.bot.reload_module("components.redeems")
        await self.bot.reload_module("components.owner_cmds")
        await self.bot.reload_module("components.listeners")
        print("Commands Reloaded")
        await ctx.send(f"Commands have been updated! wyntrvThumbup")


    # Check which modules are loaded.
    @commands.command()
    async def loaded_modules(self, ctx: commands.Context) -> None:
        print(self.bot.modules)

# This is our entry point for the module.
async def setup(bot: commands.Bot) -> None:
    component = OwnerCmds(bot)
    await bot.add_component(component)
