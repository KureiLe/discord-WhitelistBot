from turtle import pos
import disnake
from disnake.ext import commands
from disnake.utils import find
import json
from pymongo import MongoClient
import asyncio

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

async def check_if_registered(ctx):
    server_id = str(ctx.message.guild.id)
    find = col.find_one({server_id:{"$exists":True}})
    
    if find == None:
        post = {
            server_id: []
        }
        col.insert_one(post)

@bot.command()
async def whitelists(ctx):
    await check_if_registered(ctx)
    server_id = str(ctx.message.guild.id)
    find = col.find({server_id:{"$exists":True}})
    for x in find:
        array = x[server_id]
        await ctx.send(array)

@bot.command()
async def whitelist(ctx, value = ''):
    await check_if_registered(ctx)
    if value == '':
        await ctx.send('Command needs an argument (id)')
    else:
        server_id = str(ctx.message.guild.id)
        find = col.find({server_id:{"$exists":True}})
        for x in find:
            array = x[server_id]
            original_data = {server_id: array}
            if value in array:
                await ctx.send('Already whitelisted')
            else:
                async def check():
                    try:
                        bot.get_user(value)
                        return True
                    except:
                        return False
                
                if await check() == True:
                    array.append(value)
                    post = {
                        "$set": {server_id: array}
                    }
                    col.update_one(original_data, post)
                    await ctx.send('Whitelisted')
                else:
                    await ctx.send('Argument must be an id')

discord_key = read_json["discord_key"]
bot.run(discord_key)