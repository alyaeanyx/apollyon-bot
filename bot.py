import asyncio
import discord
import yaml
import feeds

config = yaml.safe_load(open("config.yaml"))
p = config["command_prefix"]
try:
    feed_channels = yaml.safe_load(open("channels.yaml"))
    print(feed_channels)
except FileNotFoundError:
    feed_channels = []

client = discord.Client()


@client.event
async def on_ready():
    for guild in client.guilds:
        print(f"Found guild: {guild.name}")
    print("Ready")


@client.event
async def on_message(message):
    if message.content.startswith(p) and message.author != client.user:
        channels_updated = False
        command = message.content[len(p):].split(" ")

        if not message.author.permissions_in(message.channel).manage_channels and command[0] != "help":
            await message.channel.send("You need to have the \"Manage channels\" permission to use this bot.")
            return

        if command[0] == "help":
            await message.channel.send(open("help.txt").read().format(p=p, d=config["maintainer"]),
                                       allowed_mentions=discord.AllowedMentions.none())

        elif command[0] == "sync" and message.author.id == config["maintainer"]:
            if not feeds.feed_exists(command[1]):
                await message.channel.send(f"Feed doesn't exist")
            feed = feeds.get_feed(command[1])
            updates = feed.get_updates()
            await message.channel.send(f"Feed synced, {len(updates)} update(s) skipped")

        elif command[0] == "syncall" and message.author.id == config["maintainer"]:
            await message.channel.send("Syncing channels...")
            for feed in feeds.FEEDS:
                updates = feed.get_updates()
                await message.channel.send(f"Channel {feed.name} synced, {len(updates)} update(s) skipped")

        elif command[0] == "list":
            msg = "*Available feeds:*\n"
            for feed in feeds.FEEDS:
                msg += f"**{feed.name}:** {feed.description}\n"
            await message.channel.send(msg)

        elif command[0] == "add" or command[0] == "remove":
            if len(command) <= 1:
                await message.channel.send(f"You need to provide a feed to this command, for instance {p}add Ana1")
                return
            feed_name = command[1]
            if not feeds.feed_exists(feed_name):
                await message.channel.send(f"Feed \"{feed_name}\" doesn't exist. Try {p}list for a list of available feeds.")
                return

            if command[0] == "add":
                for f in feed_channels:
                    if f["feed_name"] == feed_name:
                        if message.channel.id in f["channels"]:
                            await message.channel.send(f"This channel already is subscribed to **{feed_name}**.")
                            return
                        f["channels"].append(message.channel.id)
                        break
                else:
                    feed_channels.append({"feed_name": feed_name, "channels": [message.channel.id]})
                channels_updated = True
                await message.channel.send(f"Successfully subscribed #{message.channel.name} to feed **{feed_name}**.")
            elif command[0] == "remove":
                for f in feed_channels:
                    if f["feed_name"] == feed_name:
                        try:
                            f["channels"].remove(message.channel.id)
                            if len(f["channels"]) == 0:
                                feed_channels.remove(f)
                            await message.channel.send(f"Successfully unsubscribed #{message.channel.name} from feed **{feed_name}**.")
                            channels_updated = True
                        except ValueError:
                            await message.channel.send(f"This channel isn't subscribed to **{feed_name}**.")
                        break
                else:
                    await message.channel.send(f"This channel isn't subscribed to **{feed_name}**.")

        elif command[0] == "clear":
            for f in feed_channels:
                if message.channel.id in f["channels"]:
                    f["channels"].remove(message.channel.id)
                    channels_updated = True
            await message.channel.send(f"Cleared channel #{message.channel.name}.")

        else:
            await message.channel.send(f"Unknown command. Try {p}help for a full list of commands.")

        if channels_updated:
            chfile = open("channels.yaml", "w")
            yaml.dump(feed_channels, chfile)
            chfile.close()


async def background_task(c):
    await c.wait_until_ready()
    while True:
        for f in feed_channels:
            feed = feeds.get_feed(f["feed_name"])
            updates = feed.get_updates()
            for channel_id in f["channels"]:
                channel = c.get_channel(channel_id)
                for update in updates:
                    await channel.send(update)

        await asyncio.sleep(1)


client.loop.create_task(background_task(client))
client.run(config["discord_token"])
