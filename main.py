import os
import asyncio
import logging

import sqlite3
import asqlite

import twitchio
from twitchio.ext import commands
from twitchio import eventsub
from twitchio import web


# Twitch Credentials // Can convert Twitch usernames to ID @ https://www.streamweasels.com/tools/convert-twitch-username-%20to-user-id/
CLIENT_ID = 'twitch-app-id'
CLIENT_SECRET = 'twitch-app-secret'
USER_ID = 'broadcaster-id'
BOT_ID = 'bot-id'

# Twitch Auth
LOGGER: logging.Logger = logging.getLogger("Bot")

# Twitch Bot
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
    # Comment out on first run, visit http://localhost:4343/oauth?scopes=user:read:chat%20user:write:chat%20moderator:read:followers%20moderator:manage:announcements%20moderator:manage:chat_messages%20user:bot while logged into bot account, http://localhost:4343/oauth?scopes=channel:bot%20channel:manage:redemptions%20channel:read:subscriptions%20bits:read while logged into broadcaster account
    async def setup_hook(self) -> None:
        # Subscribe to read chat (event_message) from our channel as the bot...
        # This creates and opens a websocket to Twitch EventSub...
        subscription = eventsub.ChatMessageSubscription(broadcaster_user_id=USER_ID, user_id=BOT_ID)
        await self.subscribe_websocket(payload=subscription)

        # Subscribe and listen to when a stream goes live..
        subscription = eventsub.StreamOnlineSubscription(broadcaster_user_id=USER_ID)
        await self.subscribe_websocket(payload=subscription)

        # Subscirbe and listen to Reward redemptions and updates...
        subscription = eventsub.ChannelPointsRedeemAddSubscription(broadcaster_user_id=USER_ID)
        await self.subscribe_websocket(payload=subscription)

        subscription = eventsub.ChannelPointsRedeemUpdateSubscription(broadcaster_user_id=USER_ID)
        await self.subscribe_websocket(payload=subscription)

        subscription = eventsub.ChannelPointsAutoRedeemSubscription(broadcaster_user_id=USER_ID)
        await self.subscribe_websocket(payload=subscription)

        subscription = eventsub.ChannelPointsAutoRedeemV2Subscription(broadcaster_user_id=USER_ID)
        await self.subscribe_websocket(payload=subscription)

        # Subscribe and listen for Follows
        subscription = eventsub.ChannelFollowSubscription(broadcaster_user_id=USER_ID, moderator_user_id=BOT_ID)
        await self.subscribe_websocket(payload=subscription)

        # Subscribe and listen to Raids
        subscription = eventsub.ChannelRaidSubscription(to_broadcaster_user_id=USER_ID)
        await self.subscribe_websocket(payload=subscription)

        # Subscribe and listen for Subs
        subscription = eventsub.ChannelSubscribeSubscription(broadcaster_user_id=USER_ID)
        await self.subscribe_websocket(payload=subscription)

        subscription = eventsub.ChannelSubscribeMessageSubscription(broadcaster_user_id=USER_ID)
        await self.subscribe_websocket(payload=subscription)

        subscription = eventsub.ChannelSubscriptionGiftSubscription(broadcaster_user_id=USER_ID)
        await self.subscribe_websocket(payload=subscription)

        #Subscribe and listen for bit cheers
        subscription = eventsub.ChannelCheerSubscription(broadcaster_user_id=USER_ID)
        await self.subscribe_websocket(payload=subscription)

        # Load the module that contains our component, commands, and listeners.
        # Modules can have multiple components
        await self.load_module("components.owner_cmds")
        await self.load_module("components.cmds")
        await self.load_module("components.chat")
        await self.load_module("components.redeems")
        await self.load_module("components.listeners")

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

# Run Bot
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
