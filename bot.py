import asyncio
import discord
import yaml
import feeds
import traceback
import time
import datetime

config = yaml.safe_load(open("config.yaml"))
p = config["command_prefix"]
try:
    feed_channels = yaml.safe_load(open("channels.yaml"))
    print(feed_channels)
except FileNotFoundError:
    feed_channels = []

client = discord.Client()

ready = False


@client.event
async def on_ready():
    global ready
    for guild in client.guilds:
        print(f"Found guild: {guild.name}")
    print("Ready")
    ready = True


@client.event
async def on_member_update(before, after):
    if after.id == client.user.id and after.nick != config["nickname"]:
        await after.edit(nick=config["nickname"])


@client.event
async def on_message(message):
    if message.content.startswith(p) and message.author != client.user:
        channels_updated = False
        command = message.content[len(p):].split(" ")

        if not message.author.permissions_in(message.channel).manage_channels and command[0] != "help":
            if command[0] in ["sync", "syncall", "list", "add", "remove", "mention", "clear"]:
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
            await message.channel.send("Done!")

        elif command[0] == "list":
            msg = "*Available feeds:*\n"
            for feed in feeds.FEEDS:
                if feed.public:
                    msg += f"**{feed.name}:** {feed.description}\n"
            await message.channel.send(msg)

        elif command[0] == "add" or command[0] == "remove" or command[0] == "mention":
            if len(command) <= 1:
                await message.channel.send(f"You need to provide a feed to this command as an argument.")
                return
            feed_name = command[1]
            if not feeds.feed_exists(feed_name):
                await message.channel.send(f"Feed \"{feed_name}\" doesn't exist. Try {p}list for a list of available feeds.")
                return

            if command[0] == "add":
                for f in feed_channels:
                    if f["feed_name"] == feed_name:
                        if message.channel.id in [ch["id"] for ch in f["channels"]]:
                            await message.channel.send(f"This channel already is subscribed to **{feed_name}**.")
                            return
                        f["channels"].append({"id": message.channel.id, "mention": ""})
                        break
                else:
                    feed_channels.append({"feed_name": feed_name,
                                          "channels": [{"id": message.channel.id, "mention": ""}]
                                          })
                channels_updated = True
                await message.channel.send(f"Successfully subscribed #{message.channel.name} to feed **{feed_name}**.")

            elif command[0] == "remove":
                for f in feed_channels:
                    if f["feed_name"] == feed_name:
                        for ch in f["channels"]:
                            if ch["id"] == message.channel.id:
                                f["channels"].remove(ch)
                                if len(f["channels"]) == 0:
                                    feed_channels.remove(f)
                                await message.channel.send(f"Successfully unsubscribed #{message.channel.name} from feed **{feed_name}**.")
                                channels_updated = True
                                break
                        else:
                            await message.channel.send(f"This channel isn't subscribed to **{feed_name}**.")
                        break
                else:
                    await message.channel.send(f"This channel isn't subscribed to **{feed_name}**.")

            elif command[0] == "mention":
                if len(command) <= 2:
                    await message.channel.send("You need to provide a valid mention string to this command (@<role/user>)")
                    return
                for f in feed_channels:
                    if f["feed_name"] == feed_name:
                        for ch in f["channels"]:
                            if ch["id"] == message.channel.id:
                                if command[2] == "none":
                                    ch["mention"] = ""
                                else:
                                    ch["mention"] = command[2]
                                await message.channel.send(f"Updated mention settings for feed **{feed_name}** in #{message.channel.name}.")
                                channels_updated = True
                                break
                        else:
                            await message.channel.send(f"This channel isn't subscribed to **{feed_name}** yet. Use \"{p}add {feed_name}\" to do so.")
                            return
                        break
                else:
                    await message.channel.send(f"This channel isn't subscribed to **{feed_name}** yet. Use \"{p}add {feed_name}\" to do so.")
                    return

        elif command[0] == "clear":
            for f in feed_channels:
                for ch in f["channels"]:
                    if ch["id"] == message.channel.id:
                        f["channels"].remove(ch)
                        channels_updated = True
            await message.channel.send(f"Cleared channel #{message.channel.name}.")

        else:
            #await message.channel.send(f"Unknown command. Try {p}help for a full list of commands.")
            pass

        if channels_updated:
            chfile = open("channels.yaml", "w")
            yaml.dump(feed_channels, chfile)
            chfile.close()



last_error = {}

async def background_task():
    await client.wait_until_ready()
    while not ready:
        await asyncio.sleep(0.1)
    await asyncio.sleep(2)

    while True:
        for f in feed_channels:
            print("Syncing feed", f["feed_name"])
            feed = feeds.get_feed(f["feed_name"])
            try:
                updates = feed.get_updates()
            except Exception as e:
                """if feed.name in last_error:
                    delta_t = time.time() - last_error[feed.name]
                    if delta_t < config["error_timeout"]:
                        continue
                    elif delta_t > config["error_timeout"] * 4:
                        last_error["feed_name"] = time.time()
                        continue
                else:
                    continue"""
                last_error[feed.name] = time.time()
                exc = ''.join(traceback.format_exception(None, e, e.__traceback__))
                feeds.get_feed("DevLog").add_update(f"An error occurred in the update routine of **{feed.name}**:\n{exc}")

            for ch in f["channels"]:
                channel = client.get_channel(ch["id"])
                if channel.guild.id in config["blocklist"]:
                    continue

                mentioned = False
                for update in updates:
                    if ch["mention"] != "" and not mentioned:
                        await channel.send(ch["mention"] + " " + update)
                        mentioned = True
                    else:
                        await channel.send(update)
                    await asyncio.sleep(0.5)

        timestamp = datetime.datetime.now().isoformat(timespec="seconds")
        activity = discord.Activity(type=discord.ActivityType.playing, name="Last update: "+timestamp)
        try:
            await client.change_presence(activity=activity)
        except ConnectionResetError:
            pass

        for guild in client.guilds:
            if guild.me.nick != config["nickname"]:
                await guild.me.edit(nick=config["nickname"])

        await asyncio.sleep(config["fetching_interval"])


client.loop.create_task(background_task())
client.run(config["discord_token"])
