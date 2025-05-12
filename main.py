import os
import asyncio
import logging

import sqlite3
import asqlite

import twitchio
from twitchio.ext import commands
from twitchio import eventsub
from twitchio import web


#Twitch Credentials // Can convert Twitch usernames to ID @ https://www.streamweasels.com/tools/convert-twitch-username-%20to-user-id/
CLIENT_ID = 'twitch-app-id'
CLIENT_SECRET = 'twitch-app-secret'
USER_ID = 'broadcaster-id'
BOT_ID = 'bot-id'

#Websocket Stuff
WEBSOCKET = 'http://localhost:4343/'

#Twitch Auth
LOGGER: logging.Logger = logging.getLogger("Bot")

#Twitch Bot
class Bot(commands.Bot):
    def __init__(self, *, token_database: asqlite.Pool) -> None:
        self.token_database = token_database
        super().__init__(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            bot_id=BOT_ID,
            owner_id=USER_ID,
            prefix="!",
        )
    #Comment out on first run, visit http://localhost:4343/oauth?scopes=user:read:chat%20user:write:chat%20user:bot while logged into bot account,  http://localhost:4343/oauth?scopes=channel:bot while logged into broadcaster account
    async def setup_hook(self) -> None:
        # Add our component which contains our commands...
        await self.add_component(MyComponent(self))

        # Subscribe to read chat (event_message) from our channel as the bot...
        # This creates and opens a websocket to Twitch EventSub...
        subscription = eventsub.ChatMessageSubscription(broadcaster_user_id=USER_ID, user_id=BOT_ID)
        await self.subscribe_websocket(payload=subscription)

        # Subscribe and listen to when a stream goes live..
        # For this example listen to our own stream...
        subscription = eventsub.StreamOnlineSubscription(broadcaster_user_id=USER_ID)
        await self.subscribe_websocket(payload=subscription)

    async def add_token(self, token: str, refresh: str) -> twitchio.authentication.ValidateTokenPayload:
        # Make sure to call super() as it will add the tokens interally and return us some data...
        resp: twitchio.authentication.ValidateTokenPayload = await super().add_token(token, refresh)

        # Store our tokens in a simple SQLite Database when they are authorized...
        query = """
        INSERT INTO tokens (user_id, token, refresh)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id)
        DO UPDATE SET
            token = excluded.token,
            refresh = excluded.refresh;
        """

        async with self.token_database.acquire() as connection:
            await connection.execute(query, (resp.user_id, token, refresh))

        LOGGER.info("Added token to the database for user: %s", resp.user_id)
        return resp

    async def load_tokens(self, path: str | None = None) -> None:
        # We don't need to call this manually, it is called in .login() from .start() internally...

        async with self.token_database.acquire() as connection:
            rows: list[sqlite3.Row] = await connection.fetchall("""SELECT * from tokens""")

        for row in rows:
            await self.add_token(row["token"], row["refresh"])

    async def setup_database(self) -> None:
        # Create our token table, if it doesn't exist..
        query = """CREATE TABLE IF NOT EXISTS tokens(user_id TEXT PRIMARY KEY, token TEXT NOT NULL, refresh TEXT NOT NULL)"""
        async with self.token_database.acquire() as connection:
            await connection.execute(query)

    async def event_ready(self) -> None:
        LOGGER.info("Successfully logged in as: %s", self.bot_id)


class MyComponent(commands.Component):
    
    def __init__(self, bot: Bot):
        # Passing args is not required...
        # We pass bot here as an example...
        self.bot = bot
        bonkread = open("./bonks/bonks.txt", "r+")
        self.bonks = int(bonkread.read())

    # We use a listener in our Component to display the messages received.
    @commands.Component.listener()
    async def event_message(self, payload: twitchio.ChatMessage) -> None:
        print(f"[{payload.broadcaster.name}] - {payload.chatter.name}: {payload.text}")

    @commands.command(name="bonk")
    async def bonk(self, ctx: commands.Context) -> None:
        """Give 'em a bonk!

        !bonk
        """
        self.bonks += 1
        bonkwrite = open("./bonks/bonks.txt", "w")
        bonkwrite.write(str(self.bonks))
        
        await ctx.send(f"BOP {ctx.chatter.mention} bonked Wynter! He's been bonked {self.bonk} times!")

    @commands.group(invoke_fallback=True)
    async def socials(self, ctx: commands.Context) -> None:
        """Group command for our social links.

        !socials
        """
        await ctx.send("DinoDance Check out the socials! https://discord.gg/w2xNN7RS7c www.youtube.com/@WynterVT https://x.com/WynterVT")

    @commands.command(name="discord")
    async def socials_discord(self, ctx: commands.Context) -> None:
        """Sub command of socials that sends only our discord invite.

        !socials discord
        """
        await ctx.send("Join the discord! https://discord.gg/w2xNN7RS7c")

    @commands.Component.listener()
    async def event_stream_online(self, payload: twitchio.StreamOnline) -> None:
        # Event dispatched when a user goes live from the subscription we made above...
        print(f'He is Live!')

    @commands.Component.listener()
    async def event_stream_online(self, payload: twitchio.StreamOnline) -> None:
        # Event dispatched when a user goes live from the subscription we made above...
        print(f'He is Offline!')

    @commands.command(name="start")
    @commands.is_moderator()
    async def start(self, ctx: commands.Context):
        """Mod command to start the 30 min auto social post

        """
        while True:
            await ctx.send("DinoDance Check out the socials! https://discord.gg/w2xNN7RS7c https://youtube.com/@WynterVT https://x.com/WynterVT DinoDance")
            await asyncio.sleep(1800)


#Run Bot
def main() -> None:
    twitchio.utils.setup_logging(level=logging.INFO)

    async def runner() -> None:
        async with asqlite.create_pool("tokens.db") as tdb, Bot(token_database=tdb) as bot:
            await bot.setup_database()
            await bot.start()

    try:
        asyncio.run(runner())
    except KeyboardInterrupt:
        LOGGER.warning("Shutting down due to KeyboardInterrupt...")


if __name__ == "__main__":
    main()
