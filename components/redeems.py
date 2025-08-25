import asyncio
import twitchio
from twitchio.ext import commands

class Redeems(commands.Component):
    def __init__(self, bot: commands.Bot) -> None:
        # Passing args is not required...
        # We pass bot here as an example...
        self.bot = bot

    # Reward Redemptions - Preparation for bonk redemtion other than command, haven't been implemented yet
    @commands.reward_command(id="Bonk", invoke_when=commands.RewardStatus.fulfilled)
    async def reward_bonk(self, ctx: commands.Context, *, user_input: str):
        assert ctx.redemption
        print(f"Bonk has been redeemed by {ctx.author.mention} and said {user_input}")

async def setup(bot: commands.Bot) -> None:
    await bot.add_component(Redeems(bot))
