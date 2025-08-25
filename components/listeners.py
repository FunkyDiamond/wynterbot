import asyncio
import twitchio
from twitchio.ext import commands
import obsws_python as obs
import urllib.request
import boto3
from botocore.exceptions import BotoCoreError, ClientError

from TwitchWynterBot import BOT_ID
from gtts import gTTS

#Constants
RAIDER_NAME_LINK = './components/raider.txt'
RAIDER_VIEWER_LINK = './components/raidviewers.txt'
FOLLOWER_LINK = './components/follower.txt'
SUB_NAME_LINK = './components/subname.txt'
BIT_MESSAGE_LINK = './components/bitmessage.txt'
BIT_NUMBER_LINK = './components/bitnumber.txt'
BIT_NAME_LINK = './components/bitname.txt'
GIFT_NAME_LINK = './components/giftname.txt'
GIFT_NUMBER_LINK = './components/giftnumber.txt'
TWITCH_AUTH_TOKEN = 'twitchauthtoken' # Change this to a twitch auth token
OBS_IP = 'obsipaddress' # Change these to your OBS Websocket credentials
OBS_PASSWORD = 'obspassword'

def tts_speak(text: str, path: str = "./components/bits.mp3"):
    """
    Generate TTS with Amazon Polly (Generative voice).
    Falls back to gTTS if Polly fails or credentials are missing.
    """
    try:
        # Polly client will use env vars or AWS CLI config automatically
        polly = boto3.client(
        "polly",
        aws_access_key_id="aws-access-key-id", # Change these if you want to use Polly TTS, if not, it'll fallback to Google TTS
        aws_secret_access_key="aws-secret-key",
        region_name="us-east-1"
        )
        response = polly.synthesize_speech(
            Text=text,
            OutputFormat="mp3",
            VoiceId="Joanna",     # Generative voice, change if desired
            Engine="generative" # Ensure generative engine
        )

        # Save the audio stream to disk
        with open(path, "wb") as f:
            f.write(response["AudioStream"].read())

    except (BotoCoreError, ClientError, Exception) as e:
        # Fallback to gTTS if anything goes wrong
        print(f"[TTS] Polly failed ({e}), falling back to gTTS.")
        tts = gTTS(text, lang="en")
        tts.save(path)


class Listeners(commands.Component):

    def __init__(self, bot: commands.Bot):
        # Passing args is not required...
        # We pass bot here as an example...
        self.bot = bot
        self.follow_queue = asyncio.Queue()
        self.dono_queue = asyncio.PriorityQueue()

    @commands.Component.listener()
    async def event_stream_online(self, payload: twitchio.StreamOnline) -> None:
        # Event dispatched when a user goes live
        self.req = obs.ReqClient(host=OBS_IP, port=4455, password=OBS_PASSWORD, timeout=3)
        print("Stream is online!")

    @commands.Component.listener()
    async def event_stream_offline(self, payload: twitchio.StreamOffline) -> None:
        # Event dispatched when a user goes offline
        print("Stream is offline...")
    
    @commands.Component.listener()
    async def event_raid(self, payload: twitchio.ChannelRaid) -> None:
        await payload.to_broadcaster.send_announcement(moderator=BOT_ID, message=f"wyntrvWoah {payload.from_broadcaster.mention} has raided with {payload.viewer_count} viewers! Welcome to the stream! wyntrvLove", color="primary")
        raider = await payload.from_broadcaster.user()
        raidername = raider.display_name + ' approaching'
        raiderviewers = f'with {payload.viewer_count} viewers'
        raiderwrite = open(RAIDER_NAME_LINK, "w+")
        raiderwrite.write(str(raidername))
        raiderwrite.close()
        raiderviewerwrite = open(RAIDER_VIEWER_LINK, "w+")
        raiderviewerwrite.write(str(raiderviewers))
        raiderviewerwrite.close()
        url = raider.profile_image.base_url
        urllib.request.urlretrieve(url, './components/raider.jpg')
        try:
            self.req.set_source_filter_enabled("[ALERT] Raid", "START", True)
        except:
            self.req = obs.ReqClient(host=OBS_IP, port=4455, password=OBS_PASSWORD, timeout=3)
            self.req.set_source_filter_enabled("[ALERT] Raid", "START", True)
        finally:
            await asyncio.sleep(5)
        raiderwrite = open(RAIDER_NAME_LINK, "w")
        raiderwrite.write(str('Waiting...'))
        raiderwrite.close()

    @commands.Component.listener()
    async def event_follow(self, payload: twitchio.ChannelFollow):
        await self.follow_queue.put(payload)

    @commands.Component.listener()
    async def event_cheer(self, payload: twitchio.ChannelCheer):
        await self.dono_queue.put((4, payload))

    # Save Cheermote Image
    async def save_cheermote_image(self, *, broadcaster_id: str, bits: int, path: str) -> None:
        cheermotes = await self.bot.fetch_cheermotes(broadcaster_id=broadcaster_id)
        cm = next((c for c in cheermotes if c.prefix.lower() == "cheer"), cheermotes[0])
        tiers = sorted(cm.tiers, key=lambda t: t.min_bits)
        chosen = max((t for t in tiers if t.min_bits <= bits), key=lambda t: t.min_bits, default=tiers[0])
        imgset = chosen.images["dark"]["animated"]
        asset_url = imgset.get("3") or next(iter(imgset.values()))
        urllib.request.urlretrieve(asset_url, path)

    @commands.Component.listener()
    async def event_subscription(self, payload: twitchio.ChannelSubscribe):
        await self.dono_queue.put((3, payload))

    @commands.Component.listener()
    async def event_subscription_gift(self, payload: twitchio.ChannelSubscriptionGift):
        await self.dono_queue.put((1, payload))

    @commands.Component.listener()
    async def event_subscription_message(self, payload: twitchio.ChannelSubscriptionMessage):
        await self.dono_queue.put((2, payload))

    async def process_follows(self):
        while True:
            follow_data = await self.follow_queue.get()

            # Process Follow
            if hasattr(follow_data, 'followed_at'):
                await follow_data.broadcaster.send_message(f"Thank you for the follow {follow_data.user.mention} wyntrvLove", BOT_ID)
                followername = follow_data.user.display_name + ' Followed!'
                raiderwrite = open(FOLLOWER_LINK, "w+")
                raiderwrite.write(str(followername))
                raiderwrite.close()
                try:
                    self.req.set_source_filter_enabled("[ALERT] Follow", "FOLLOWSTART", True)
                except:
                    self.req = obs.ReqClient(host=OBS_IP, port=4455, password=OBS_PASSWORD, timeout=3)
                    self.req.set_source_filter_enabled("[ALERT] Follow", "FOLLOWSTART", True)
                finally:
                    await asyncio.sleep(4)

            # Error in Task Queue
            else:
                await follow_data.broadcaster.send_message(f"Something isn't right...", BOT_ID)
            self.follow_queue.task_done()

    async def process_donos(self):
        while True:
            priority, dono_data = await self.dono_queue.get()

            # Process Subs
            if hasattr(dono_data, 'gift'):
                await dono_data.broadcaster.send_message(f"{dono_data.user.mention} has just subscibed! wyntrvLove", BOT_ID)
                subname = dono_data.user.display_name
                subwrite = open(SUB_NAME_LINK, "w+")
                subwrite.write(str(subname))
                subwrite.close()
                try:
                    self.req.set_source_filter_enabled("[ALERT] Dono", "SUBSTART", True)
                except:
                    self.req = obs.ReqClient(host=OBS_IP, port=4455, password=OBS_PASSWORD, timeout=3)
                    self.req.set_source_filter_enabled("[ALERT] Dono", "SUBSTART", True)
                finally:
                    await asyncio.sleep(5)

            # Process ReSubs
            elif hasattr(dono_data, 'months'):
                # Subs w/ message
                await dono_data.broadcaster.send_message(f"{dono_data.user.mention} has just subscibed! wyntrvLove They've been subbed for {dono_data.months} months! wyntrvWoah", BOT_ID)

            # Process Gift Subs
            elif hasattr(dono_data, 'total'):
                # Anon Gift
                if dono_data.anonymous == True:
                    await dono_data.broadcaster.send_message(f"A very generous chatter has just gifted {dono_data.total} subs! wyntrvWoah wyntrvLove", BOT_ID)
                    giftname = 'Anonymous'
                    giftnumber = f'{dono_data.total}'
                    giftnamewrite = open(GIFT_NAME_LINK, "w+")
                    giftnamewrite.write(str(giftname))
                    giftnamewrite.close()
                    giftnumberwrite = open(GIFT_NUMBER_LINK, "w+")
                    giftnumberwrite.write(str(giftnumber))
                    giftnumberwrite.close()
                    try:
                        self.req.set_source_filter_enabled("[ALERT] Dono", "GIFTSTART", True)
                    except:
                        self.req = obs.ReqClient(host=OBS_IP, port=4455, password=OBS_PASSWORD, timeout=3)
                        self.req.set_source_filter_enabled("[ALERT] Dono", "GIFTSTART", True)
                    finally:
                        await asyncio.sleep(5)

                # User Gift
                else:
                    await dono_data.broadcaster.send_message(f"{dono_data.user.mention} has just gifted {dono_data.total} subs! wyntrvLove", BOT_ID)
                    giftname = f'{dono_data.user.display_name}'
                    giftnumber = f'{dono_data.total}'
                    giftnamewrite = open(GIFT_NAME_LINK, "w+")
                    giftnamewrite.write(str(giftname))
                    giftnamewrite.close()
                    giftnumberwrite = open(GIFT_NUMBER_LINK, "w+")
                    giftnumberwrite.write(str(giftnumber))
                    giftnumberwrite.close()
                    try:
                        self.req.set_source_filter_enabled("[ALERT] Dono", "GIFTSTART", True)
                    except:
                        self.req = obs.ReqClient(host=OBS_IP, port=4455, password=OBS_PASSWORD, timeout=3)
                        self.req.set_source_filter_enabled("[ALERT] Dono", "GIFTSTART", True)
                    finally:
                        await asyncio.sleep(5)
                        
            # Process Bits
            elif hasattr(dono_data, 'bits'):
                if dono_data.bits > 499:
                    # Bits Message
                    if dono_data.message != None:
                        message = {dono_data.message}
                        await dono_data.broadcaster.send_message(f"Thank you for the {dono_data.bits} bits, {dono_data.user.mention} ! wyntrvLove", BOT_ID)
                        # Save TTS
                        tts_speak(f"{message}", "./components/bits.mp3")
                        # Write Text Files
                        bitmessage = f'{dono_data.user.display_name}\n{message}'
                        bitnumber = dono_data.bits
                        bitmessagewrite = open(BIT_MESSAGE_LINK, "w+")
                        bitmessagewrite.write(str(bitmessage))
                        bitmessagewrite.close()
                        bitnumberwrite = open(BIT_NUMBER_LINK, "w+")
                        bitnumberwrite.write(str(bitnumber))
                        bitnumberwrite.close()
                        # Save Cheermote
                        await self.save_cheermote_image(
                                broadcaster_id = dono_data.broadcaster.id,
                                bits = bitnumber,
                                path = "./components/cheermote.gif",
                                )
                        try:
                            self.req.set_source_filter_enabled("[ALERT] Dono", "BITMESSAGESTART", True)
                        except:
                            self.req = obs.ReqClient(host=OBS_IP, port=4455, password=OBS_PASSWORD, timeout=3)
                            self.req.set_source_filter_enabled("[ALERT] Dono", "BITMESSAGESTART", True)
                        finally:
                            await asyncio.sleep(10)
                    # Bits No Message
                    else:
                        await dono_data.broadcaster.send_message(f"Thank you for the {dono_data.bits} bits, {dono_data.user.mention} ! wyntrvLove", BOT_ID)
                        # Write Text Files
                        bitname = dono_data.user.display_name
                        bitnumber = dono_data.bits
                        bitnamewrite = open(BIT_NAME_LINK, "w+")
                        bitnamewrite.write(str(bitname))
                        bitnamewrite.close()
                        bitnumberwrite = open(BIT_NUMBER_LINK, "w+")
                        bitnumberwrite.write(str(bitnumber))
                        bitnumberwrite.close()
                        # Save Cheermote
                        await self.save_cheermote_image(
                                broadcaster_id = dono_data.broadcaster.id,
                                bits = bitnumber,
                                path = "./components/cheermote.gif",
                                )
                        try:
                            self.req.set_source_filter_enabled("[ALERT] Dono", "BITSTART", True)
                        except:
                            self.req = obs.ReqClient(host=OBS_IP, port=4455, password=OBS_PASSWORD, timeout=3)
                            self.req.set_source_filter_enabled("[ALERT] Dono", "BITSTART", True)
                        finally:
                            await asyncio.sleep(5)
                # Bits Under 500
                else:
                    await dono_data.broadcaster.send_message(f"Thank you for the {dono_data.bits} bits, {dono_data.user.mention} ! wyntrvLove", BOT_ID)
                    # Write Text Files
                    bitname = dono_data.user.display_name
                    bitnumber = dono_data.bits
                    bitnamewrite = open(BIT_NAME_LINK, "w+")
                    bitnamewrite.write(str(bitname))
                    bitnamewrite.close()
                    bitnumberwrite = open(BIT_NUMBER_LINK, "w+")
                    bitnumberwrite.write(str(bitnumber))
                    bitnumberwrite.close()
                    # Save Cheermote
                    await self.save_cheermote_image(
                            broadcaster_id = dono_data.broadcaster.id,
                            bits = bitnumber,
                            path = "./components/cheermote.gif",
                            )
                    try:
                        self.req.set_source_filter_enabled("[ALERT] Dono", "BITSTART", True)
                    except:
                        self.req = obs.ReqClient(host=OBS_IP, port=4455, password=OBS_PASSWORD, timeout=3)
                        self.req.set_source_filter_enabled("[ALERT] Dono", "BITSTART", True)
                    finally:
                        await asyncio.sleep(5)

            # Error in Task Queue
            else:
                await dono_data.broadcaster.send_message(f"Something isn't right...", BOT_ID)
            self.dono_queue.task_done()


async def setup(bot: commands.Bot) -> None:
    component = Listeners(bot)
    await bot.add_component(component)
    asyncio.create_task(component.process_follows())
    asyncio.create_task(component.process_donos())
