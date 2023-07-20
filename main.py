import discord
import dotenv
import subprocess
import json

def main():
    config = dotenv.dotenv_values(".env")

    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        print("{} is running.".format(client.user))

    @client.event
    async def on_message(item):
        if item.author == client.user or item.channel.name != "bot-spam":
            return

        msg = str(item.content)
        if msg[0] == "!":
            cmd = msg[1:].split(" ")[0]
            msg = msg[1:].split(" ")[1:]
            if (cmd == "p" or cmd == "profile") and len(msg) == 1:
                shell = ["dotnet", "run", "--", "profile", msg[0], config["ID"], config["SECRET"], "-r", "2" , "-j"]
                print(" ".join(shell))
                process = subprocess.Popen(shell, cwd=config["PC_PATH"], stdout=subprocess.PIPE)
                thread = await item.channel.create_thread(name=msg[0], type=discord.ChannelType.public_thread)
                for line in iter(process.stdout.readline, b''):
                    try:
                        objson = json.loads(line)
                        break
                    except:
                        await thread.send(line.decode("utf-8"))
                        continue
                
                for key in objson.keys():
                    if key == "Scores":
                        continue
                    await thread.send("{}: {}".format(key, objson[key]))
                
                embeds = []
                for score in objson["Scores"]:
                    embed = discord.Embed(description="Combo: {}".format())
                    # {'BeatmapId': 1181952, 'BeatmapName': 'Halozy - Snow Changes to a Beat Again (BoberOfDarkness) [Blizzard]', 'Combo': 339, 'Accuracy': 99.75369458128078, 'MissCount': 0.0, 'Mods': [], 'LivePp': 194.243, 'LocalPp': 194.2392055189923, 'PositionChange': 0}
                    embed.set_author(name=score["BeatmapName"], url="https://osu.ppy.sh/b/{}".format(score["BeatmapId"]))
                    embeds.append(embed)
                await thread.send(embeds=embeds)

            elif (cmd == "l" or cmd == "list"):
                shell = ["git", "branch", "-q"]
                print(" ".join(shell))
                process = subprocess.Popen(shell, cwd=config["OSU_PATH"], stdout=subprocess.PIPE)
                thread = await item.channel.create_thread(name="git branch", type=discord.ChannelType.public_thread)
                for line in iter(process.stdout.readline, b''):
                    await thread.send(line.decode("utf-8"))
            elif (cmd == "h" or cmd == "help"):
                await item.channel.send("Hello, World!")

    client.run(config["TOKEN"])

if __name__ == "__main__":
    main()
