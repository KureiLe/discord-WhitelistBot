import disnake
from disnake.ext.commands import has_permissions, MissingPermissions
from disnake.ext import commands
from disnake.utils import find
import json
from pymongo import MongoClient

intents = disnake.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="$", intents=intents, help_command=None)
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

async def check_if_registered_event(member):
    server_id = str(member.guild.id)
    find = col.find_one({server_id: {"$exists": True}})
    if find == None:
        post = {
            server_id: []
        }
        col.insert_one(post)

async def check(id):
    if await bot.fetch_user(id) != None:
        return True
    else:
        return False

@bot.event
async def on_member_join(member):
    await check_if_registered_event(member)
    user_id = member.id
    server_id = str(member.guild.id)
    find = col.find({server_id:{"$exists":True}})
    for x in find:
        id_array = x[server_id]
    if user_id not in id_array:
        await member.send('You are not whitelisted. Ask owner/mods for permission to enter the server, and then rejoin')
        await member.guild.kick(member, reason='Not Whitelisted')

@bot.command()
async def help(ctx):
    embed = disnake.Embed(title="Help Commands", color=0xF3FF47)
    embed.add_field(name="list", value="Shows list of whitelisted ID", inline=True)
    embed.add_field(name="whitelist (User ID)", value="Whitelists ID", inline=True)
    embed.add_field(name="unwhitelist (User ID)", value="Unwhitelists ID", inline=True)
    embed.set_footer(text="prefix = '$'")
    await ctx.send(embed=embed)

@bot.command()
async def list(ctx):
    await check_if_registered(ctx)
    server_id = str(ctx.message.guild.id)
    find = col.find({server_id: {"$exists": True}})
    for x in find:
        id_array = x[server_id]
    if len(id_array) != 0:
        msg = ''
        for x in id_array:
            username = await bot.fetch_user(x)
            msg += f'{username} - {x}\n'
        await ctx.send(msg)
    else:
        await ctx.send('Noone is whitelisted')

@bot.command()
@has_permissions(administrator=True)
async def whitelist(ctx, value=''):
    await check_if_registered(ctx)
    if value == '':
        await ctx.send('Command needs an argument (id)')
    else:
        if await check(value) == True:
            server_id = str(ctx.message.guild.id)
            find = col.find({server_id: {"$exists": True}})
            for x in find:
                array = x[server_id]
                original_data = {server_id: list(array)}
            if value in array:
                await ctx.send('Already whitelisted')
            else:
                array.append(value)
                post = {
                    "$set": {server_id: array}
                }
                col.update_one(original_data, post)
                await ctx.send('Whitelisted')
        else:
            await ctx.send('Argument must be an id')
@whitelist.error
async def whitelist_error(ctx, error):
    if isinstance(error, MissingPermissions):
        await ctx.send('Need Administrator Perms')

@bot.command()
@has_permissions(administrator=True)
async def unwhitelist(ctx, value=''):
    await check_if_registered(ctx)
    if value == '':
        await ctx.send('Command needs an argument (id)')
    else:
        server_id = str(ctx.message.guild.id)
        find = col.find({server_id: {"$exists": True}})
        for x in find:
            array = x[server_id]
            original_data = {server_id: list(array)}
        if value not in array:
            await ctx.send('Already not whitelisted')
        else:
            if await check(value) == True:
                array.remove(value)
                post = {
                    "$set": {server_id: array}
                }
                col.update_one(original_data, post)
                await ctx.send('Unwhitelisted')
            else:
                await ctx.send('Argument must be an id')
@unwhitelist.error
async def unwhitelist_error(ctx, error):
    if isinstance(error, MissingPermissions):
        await ctx.send('Need Administrator Perms')

discord_key = read_json["discord_key"]
bot.run(discord_key)