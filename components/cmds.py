import os
import asyncio
import twitchio
from twitchio.ext import commands

# Chat Commands
class Commands(commands.Component):
    
    # Variables
    loop = False

    def __init__(self, bot: commands.Bot):
        # Passing args is not required...
        # We pass bot here as an example...
        self.bot = bot


    # Help command that shows available commands that users can use
    @commands.command(name="help")
    async def help(self, ctx: commands.Context) -> None:
        await ctx.reply("Here's a list of available commands: [!bonk @chatter] [!socials] [!discord]")

    # BONK - Keeps track of ALL user bonks
    @commands.command(name="bonk")
    async def bonk(self, ctx: commands.Context, user: twitchio.User) -> None:
        """Give 'em a bonk!

        !bonk
        """
        if user.mention == "@WyntrVT": # Put the Streamer here!
            bonklink = f'./components/bonks/{user.display_name}.txt'
            bonkread = open(bonklink, "r+")
            self.bonks = int(bonkread.read())
            self.bonks += 1
            bonkwrite = open(bonklink, "w")
            bonkwrite.write(str(self.bonks))
            await ctx.send(f"BOP {ctx.chatter.mention} bonked Wynter! He's been bonked {self.bonks} times!")
            bonkwrite.close()
        elif user.mention == "@WyntrBot": # Put the Bot here!
            await ctx.send(f"BOP {ctx.chatter.mention} tried to bonk {user.mention} , but it was deflected! wyntrvWoah")
        elif user.mention == ctx.chatter.mention:
            await ctx.reply("You shouldn't bonk yourself, silly!")
        else:
            userbonklink = f'./components/bonks/{user.display_name}.txt'
            if os.path.exists(userbonklink):
                userbonkread = open(userbonklink, "r+")
                self.userbonks = int(userbonkread.read())
                self.userbonks += 1
                userbonkwrite = open(userbonklink, "w")
                userbonkwrite.write(str(self.userbonks))
                await ctx.send(f"BOP {ctx.chatter.mention} bonked {user.mention} ! They've been bonked {self.userbonks} times!")
                userbonkwrite.close()
            else:
                self.userbonks = 1
                userbonkwrite = open(userbonklink, "w+")
                userbonkwrite.write(str(self.userbonks))
                await ctx.send(f"BOP {ctx.chatter.mention} bonked {user.mention} ! They've been bonked {self.userbonks} time!")
                userbonkwrite.close()

    # Socials Command
    @commands.group(invoke_fallback=True)
    async def socials(self, ctx: commands.Context) -> None:
        """Group command for our social links.

        !socials
        """
        await ctx.send("DinoDance Check out the socials! https://discord.wyntervt.com/ https://youtube.wyntervt.com/ https://x.wyntervt.com/ https://vods.wyntervt.com/ DinoDance")

    # Socials Group Commands
    @socials.command(name="discord")
    async def socials_discord(self, ctx: commands.Context) -> None:
        """Sub command of socials that sends only our discord invite.

        !socials discord
        """
        await ctx.send("DinoDance Join the discord! https://discord.wyntervt.com/ DinoDance")

    @socials.command(name="x")
    async def socials_x(self, ctx: commands.Context) -> None:
        """Sub command of socials that sends only X link.

        !socials x
        """
        await ctx.send("DinoDance Follow on X! https://x.wyntervt.com/ DinoDance")

    @socials.command(name="youtube")
    async def socials_youtube(self, ctx: commands.Context) -> None:
        """Sub command of socials that sends only youtube links.

        !socials youtube
        """
        await ctx.send("DinoDance Check out some videos! https://youtube.wyntervt.com/ https://vods.wyntervt.com/ DinoDance")


    # Event Loop Toggle
    @commands.command(name="toggle")
    @commands.is_moderator()
    async def toggle(self, ctx: commands.Context):
        """Mod command to toggle the 1 hour auto social post

        """
        if self.loop:
            print("Loop Running! Stopping Loop...")
            self.loop = False
            await ctx.send("Okay, I'll stop FallCry")
        else:
            self.loop = True
            while self.loop:
                await ctx.send("DinoDance Check out the socials! https://discord.wyntervt.com/ https://youtube.wyntervt.com/ https://x.wyntervt.com/ DinoDance",)
                await asyncio.sleep(3600)
            

async def setup(bot: commands.Bot) -> None:
    await bot.add_component(Commands(bot))
