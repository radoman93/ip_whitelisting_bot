# IMPORT DISCORD.PY. ALLOWS ACCESS TO DISCORD'S API.
from decouple import config
from database import find, add, update
from pprint import pprint
import requests
import json
import os



# IMPORT COMMANDS FROM THE DISCORD.EXT MODULE.
from discord.ext import commands

# CREATES A NEW BOT OBJECT WITH A SPECIFIED PREFIX. IT CAN BE WHATEVER YOU WANT IT TO BE.
bot = commands.Bot(command_prefix="!")



token = 'Y0JkGB7szW4728N1xVU2w6ZyeAniz6H1'
hetznez_apitoken = 'y866YuXCSNMzzqUhKsYhAJFAA050R0bDp4yOheHfeIcA9WBajrm1bPWVzfwxZHee'
hetznerapi_url = "https://api.hetzner.cloud/v1/firewalls/424693"

headers = {
    'Authorization': f'Bearer {hetznez_apitoken}'
}
# Get Existing firewall settings
def getusedipaddress():
    url = hetznerapi_url

    payload = {}

    response = requests.request("GET", url, headers=headers, data=payload).json()
    rules = response['firewall']['rules']
    return (rules)


# Set New Firewall Settings
def setnewrules(rules):
    url = f"{hetznerapi_url}/actions/set_rules"
    payload = json.dumps(rules)
    response = requests.request("POST", url, headers=headers, data=payload).json()
    return response


@bot.command(
	brief="Collects the Ip address after the command for whitelisting"
)
async def IP(ctx, arg):
    pprint(ctx.author.id)
    user_details = {"user_id":f"{ctx.author.id}", "ip":f"{arg}"}

    existing_ip_address_array = getusedipaddress()
    arrays_of_ip = existing_ip_address_array[0]['source_ips']

    existUser_id = find({"user_id":f"{ctx.author.id}"})
    existIp = find({"ip":f"{arg}"})


    if existIp:
        await ctx.channel.send("Ip address exists")
    elif existUser_id:
        arrays_of_ip.remove(f"{existUser_id['ip']}/32")
        arrays_of_ip.append(f"{arg}/32")
        rules = {
            "rules": [
                {
                    "description": "Give Access to any port",
                    "direction": "in",
                    "port": "any",
                    "protocol": "tcp",
                    "source_ips": arrays_of_ip
                }
            ]
        }

        addtorule = setnewrules(rules)
        try:
            isError = addtorule['error']
        except:
            isError = False

        if isError:
            await ctx.channel.send("Invalid Ip address")
        else:
            await ctx.channel.send(f"Your binded ip address is {arg}")
            update({"user_id":f"{ctx.author.id}"}, user_details)

    else:
        arrays_of_ip.append(f"{arg}/32")
        rules = {
                "rules": [
                    {
                        "description": "Give Access to any port",
                        "direction": "in",
                        "port": "any",
                        "protocol": "tcp",
                        "source_ips": arrays_of_ip
                    }
                ]
            }

        addtorule = setnewrules(rules)
        try:
            isError = addtorule['error']
        except:
            isError = False

        if isError:
            await ctx.channel.send("Invalid Ip address")
        else:
            await ctx.channel.send("Ip address added Successfully")
            add(user_details)


bot.run(token)
