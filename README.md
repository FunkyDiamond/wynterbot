
<br/>
<div align="center">
<a href="https://github.com/ShaanCoding/ReadME-Generator">
<img src="https://i.postimg.cc/4dnR9JSF/Letter-Logo.png" alt="Logo" width="80" height="80">
</a>
<h3 align="center">Wynter Twitch Bot</h3>
<p align="center">
Configurable Twitch bot used for Wynter written in python using twitchio.
<br/>
<br/>
<a href="https://www.twitch.tv/wyntrvt/"><strong>Wynter Twitch »</strong></a>

  


</p>
</div>

## About The Project

![Product Screenshot](https://i.postimg.cc/GtVHf4M4/Twitch-Banner.png)

Being frustrated with the limitations and costs of commercial twitch bots, I decided my first 'learning python' project would be this Dockerized Twitch Bot.

This bot uses twitchio for api and command handling, making it very easy to add commands and functionality to the bot.

The initial intent was to use this bot as a way to post Discord notifications, but haven't figured out how to make them work together -- I still have LOTS to learn.

After being configured and tokens have been created to the database, the included Dockerfile can be used to build a docker image of your configuration and run in a container.

Be sure to read through all modules to fill in your credentials and better understand how the bot functions

### Built With

3rd party libraries used:

- [twitchio3](https://twitchio.dev/en/latest/)
- [asqlite](https://github.com/Rapptz/asqlite)
## Getting Started

Should be simple to get started and running, I've also included a Dockerfile to build an image to run in Docker.

The following will be under the assumption that your a budding streamer and know little to nothing about coding/python.

As always, be sure to review any code before running it on your machine.
### Prerequisites

You'll need Python3 and some sort of editor, I personally used Visual Studio Coder

**You'll also need to make a 2nd twitch account, this will be your bot account**

- python - linux
  ```sh
  sudo apt install python3-full
  ```
Full is needed if you plan to use virtual environments

- python - windows

python can be downloaded from https://www.python.org 

if you're using VS Coder, there is a Python extension that can handle your environment and versions for you.

- (Optional) Docker - linux
```sh
sudo apt install docker
```
Docker Desktop can be used for Windows

Used if you want to run this bot as a container.
### Installation

_Let's start by getting our Twitch API credentials and pulling the repository_

1. Register a new application at [https://dev.twitch.tv](https://dev.twitch.tv/), you'll need to connect you twitch account
2. Take note of the Client Id and Client Secret towards the bottom of the page, save them as we'll need them for later
(if you do not see a secret, press the 'New Secret' button)
2. Clone the repo
   ```sh
   git clone https://github.com/FunkyDiamond/wynterbot
   ```
3. Install python libraries in cloned directory. Make a virtual environment if you're not using VS Coder.
   ```sh
   pip install -U twitchio --pre asqlite twitchio[starlette]
   ```
4. Enter your keys and ids into the variables towards the top of main.py
   ```py
   #Twitch Credentials // Can convert Twitch usernames to ID @ https://www.streamweasels.com/tools/convert-twitch-username-%20to-user-id/
   CLIENT_ID = 'twitch-app-id'
   CLIENT_SECRET = 'twitch-app-secret'
   USER_ID = 'broadcaster-id'
   BOT_ID = 'bot-id'
   ```

5. Comment out the setup_hook section, like so:

From
```py
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
```

to

```py
    #Comment out on first run, visit http://localhost:4343/oauth?scopes=user:read:chat%20user:write:chat%20user:bot while logged into bot account,  http://localhost:4343/oauth?scopes=channel:bot while logged into broadcaster account
#    async def setup_hook(self) -> None:
        # Add our component which contains our commands...
#        await self.add_component(MyComponent(self))

        # Subscribe to read chat (event_message) from our channel as the bot...
        # This creates and opens a websocket to Twitch EventSub...
#        subscription = eventsub.ChatMessageSubscription(broadcaster_user_id=USER_ID, user_id=BOT_ID)
#        await self.subscribe_websocket(payload=subscription)

        # Subscribe and listen to when a stream goes live..
        # For this example listen to our own stream...
#       subscription = eventsub.StreamOnlineSubscription(broadcaster_user_id=USER_ID)
#       await self.subscribe_websocket(payload=subscription)
```

We need to do this to save tokens to the database.

7. Run the script

While in the cloned directory:
```sh
python3 main.py
```

You should see something like this in the terminal:
```sh
Generated App Token for Client-ID: 'your-client-id'
```

8. Connect your accounts!
- Log into your bot account on twitch and go to http://localhost:4343/oauth?scopes=user:read:chat%20user:write:chat%20moderator:read:followers%20moderator:manage:announcements%20moderator:manage:chat_messages%20user:bot
- Log out of your bot account and into your main, broadcaster account and go to http://localhost:4343/oauth?scopes=channel:bot%20channel:manage:redemptions%20channel:read:subscriptions
- if you see this in your terminal, you're looking good!
```sh
Added token to the database for user: 'bot-id'
Added token to the database for user: 'broadcaster-id'
```

9. Stop the script using a stop command or ctrl+c

10. Uncomment the setup_hook section

And that's it! The next time you run the script, the bot will connect to your channel and listen for events such as going live, chatter messages, cheers, etc.

At this point, you can build the docker image and run a container with your bot on it! Ensure that the "/components/" folder is mounted in your container as "/components"


## Usage

Commands can be added and edited using the py files in "./components". after adding or editing, use the !reload command in your cat to hot reload all modules!

More documentation can be found at https://twitchio.dev/en/latest/

Referring to the other commands under the MyComponent class can help with understanding how they're structured

### Docker

Only after adding the tokens to your database should you build the docker image. I was experiencing some funkiness when dockerizing first

The Dockerfile will push the python script, database files, and install needed libraries to the docker image

Mount your "./components" directory to "/components" so the bot can load your modules and save images, tts, and text files

## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request
## License

Distributed under the MIT License. See [MIT License](https://opensource.org/licenses/MIT) for more information.
## Contact

Torrin Carter - [@torrincarter](https://twitter.com/torrincarter) - tech@torrincarter.com

Project Link: [https://github.com/FunkyDiamond/wynterbot](https://github.com/FunkyDiamond/wynterbot)
