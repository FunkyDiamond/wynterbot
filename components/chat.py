import twitchio
from twitchio.ext import commands

#Constants
NICETRY = './components/nicetry.txt'
NICE = './components/nice.txt'

class Chat(commands.Component):
    def __init__(self, bot: commands.Bot) -> None:
        # Passing args is not required...
        # We pass bot here as an example...
        self.bot = bot
        nicetryread = open(NICETRY, "r+")
        self.nicetry = int(nicetryread.read())
        niceread = open(NICE, "r+")
        self.nice = int(niceread.read())

    @commands.Component.listener()
    async def event_message(self, payload: twitchio.ChatMessage) -> None:
        nice = "Nice!"
        nice_try = "Nice Try!"
        message = f"{payload.text}"

        if message == nice:
            print(f"[{payload.broadcaster.name}] - {payload.chatter.name}: {payload.text}")
            self.nice += 1
            nicewrite = open(NICE, "w+")
            nicewrite.write(str(self.nice))
            nicewrite.close()
            await payload.broadcaster.send_message(
                    sender=self.bot.bot_id,
                    message=f"wyntrvThumbup Chat found that nice {self.nice} times!",
            )
        elif message == nice_try:
            print(f"[{payload.broadcaster.name}] - {payload.chatter.name}: {payload.text}")
            self.nicetry += 1
            nicetrywrite = open(NICETRY, "w+")
            nicetrywrite.write(str(self.nicetry))
            nicetrywrite.close()
            await payload.broadcaster.send_message(
                    sender=self.bot.bot_id,
                    message=f"wyntrvSmug Wynter has had {self.nicetry} nice tries!",
            )
        else:
            print(f"[{payload.broadcaster.name}] - {payload.chatter.name}: {payload.text}")

async def setup(bot: commands.Bot) -> None:
    await bot.add_component(Chat(bot))
