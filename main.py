import disnake
from disnake.ext import commands
from disnake.utils import find
import json
from pymongo import MongoClient

bot = commands.Bot(command_prefix="$")
json_file = open("config.json").read()
read_json = json.loads(json_file)

mongo = MongoClient(read_json["pymongo_link"])
database = mongo["discord"]
col = database["data"]

@bot.event
async def on_ready():
    bot_id = bot.user.id
    print(f"logged in as {bot_id}")

@bot.command()
async def register(ctx):
    server_id = str(ctx.message.guild.id)
    find = col.find_one({server_id:{"$exists":True}})
    
    if find == None:
        post = {
            server_id: []
        }
        col.insert_one(post)
        await ctx.send('Registered')
    else:
        await ctx.send('Already registered')

discord_key = read_json["discord_key"]
bot.run(discord_key)