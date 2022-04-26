from fileinput import filename
from http import server
import gspread
import discord
from discord.ext import commands
import config
from collections import defaultdict

sa = gspread.service_account(filename="cloudconfig.json")
sh = sa.open_by_key('1nkwrHRAG1X9RgGu7h4iAkkC6qHhpTMhz5Zvq9gmjOBo')

greetssheet = sh.worksheet("1")
serverssheet = sh.worksheet("2")

print(f"{greetssheet.row_count}  {greetssheet.col_count}")
print(greetssheet.acell("A5").value)

intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix="$", intents=intents, case_insensitive=True, help_command=None)

print(serverssheet.get_all_values())

@client.event
async def on_ready():
    print("Bot is ready")
# print(wks.get_all_records())

@client.event
async def on_guild_join(guild):
    servers = serverssheet.get_all_values()
    for arr in servers:
        if "i"+str(guild.id) in arr: return
    serverssheet.update(f"A{len(servers)+1}", "i"+str(guild.id))
    serverssheet.update(f"C{len(servers)+1}", "i0")


# Command to set an action (role giving) on emoji click on specific message  
@client.command()
async def setWelcomeChannel(message):
    try:
        servers = serverssheet.get_all_values()
        i = 1
        for arr in servers:
            if "i"+str(message.guild.id) in arr:
                break
            i+=1
        serverssheet.update(f"B{i}", "i"+str(message.channel.id))
        
        embed = discord.Embed(title=f"Set channel {message.channel} to default!", color=discord.Color.green())
        await message.channel.send(embed=embed)
    except Exception as e:
        print(e)
        embed = discord.Embed(title="ERROR", description="Role syntax: `$setWelcomeChannel`", color=discord.Color.red())
        await message.channel.send(embed=embed)

@client.event
async def on_member_join(member):
    # Channel's id is now general in the test server
    embed = discord.Embed(title=f"Welcome, {member.name}!", color=discord.Color.blue())
    embed.set_image(url=member.avatar_url)
    
    servers = serverssheet.get_all_values()
    server = []
    i = 0
    factNumber = 0
    for arr in servers:
        if "i"+str(member.guild.id) in arr:
            server = arr
            factNumber = int(arr[-1].replace("i", ""))
            serverssheet.update(f"C{i}", "i"+str(factNumber+1))
            break
        i+=1
    greetings = greetssheet.get_all_values()
    if len(greetings) == 0: return
    greeting = greetings[factNumber][0]
    embed = discord.Embed(title=f"{member.name} joined the server!", description=greeting, color=discord.Color.blue())
    channel = client.get_channel(int(server[1].replace("i", "")))
    await channel.send(embed=embed)

client.run(config.TOKEN)
