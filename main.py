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

            if (cmd == "p" or cmd == "profile") and len(msg) >= 1:
                shell = ["dotnet", "run", "--", "profile", msg[0], config["ID"], config["SECRET"], "-r", "2" , "-j"]
                print(" ".join(shell))
                process = subprocess.Popen(shell, cwd=config["PC_PATH"], stdout=subprocess.PIPE)
                thread = await item.channel.create_thread(name=msg[0], type=discord.ChannelType.public_thread)
                try:
                    for line in iter(process.stdout.readline, b''):
                        try:
                            objson = json.loads(line)
                            break
                        except:
                            await thread.send(line.decode("utf-8"))
                            continue
                    if type(objson) != dict:
                        return

                    for key in objson.keys():
                        if key == "Scores":
                            continue
                        await thread.send("{}: {}".format(key, objson[key]))
                    
                    for score in objson["Scores"]:
                        await thread.send(score["Combo"])
                except:
                    error = "An error has occurred."
                    print(error)
                    await thread.send(error)

            elif cmd == "l" or cmd == "list":
                shell = ["git", "for-each-ref", "--format=%(refname:short)", "refs/heads/"]
                process = subprocess.Popen(shell, cwd=config["OSU_PATH"], stdout=subprocess.PIPE)
                text = ""
                for line in iter(process.stdout.readline, b''):
                    text += "{}, ".format(line.decode("utf-8").strip())
                await item.channel.send(text[:len(text) - 2])

            elif cmd == "h" or cmd == "help":
                await item.channel.send("Hello, World!")

    client.run(config["TOKEN"])

if __name__ == "__main__":
    main()
