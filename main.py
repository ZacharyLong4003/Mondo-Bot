import asyncio
import config
import os
import discord
import random
import time
import math
from discord.ext import tasks, commands
from datetime import datetime

# Discord API
intents = discord.Intents().all()
bot = commands.Bot(command_prefix="m!", intents=intents)

# File
LEADERBOARD_FILE = "leaderboard.txt"
CHANNEL_ID = config.CHANNEL_ID
GUILD_ID = config.GUILD_ID
secret_token = config.secret_token

#Challenge
challenge = "None"
start_time = 0
duration = 60 
max_points = 1000
answered_correctly = set()
answered_incorrectly = set()

def save_leaderboard(leaderboard_dir):
    """Saves the leaderboard to a file"""
    with open(leaderboard_dir, 'w') as file:
        for user_id, points in lb.items():
            file.write(f"{user_id}:{points}\n")

def load_leaderboard(leaderboard_dir):
    """Loads the leaderboard from a file"""
    global lb
    if os.path.exists(leaderboard_dir):
        with open(leaderboard_dir, 'r') as file:
            lb = {int(uid): int(pts) for uid, pts in (line.strip().split(":") for line in file)}
    else:
        print(f"Could not open leaderboard.")
        lb = {}

def update_leaderboard(user_id, points):
    lb[user_id] = lb.get(user_id, 0) + points
    save_leaderboard(LEADERBOARD_FILE)

async def awardChampion():
    guild = bot.get_guild(GUILD_ID)
    max_user = max(lb, key=lb.get)
    member = guild.get_member(max_user)
    role = discord.utils.get(guild.roles, name="Champion of the Server")
    if member and role:
        for m in guild.members:
            if role in m.roles:
                await m.remove_roles(role)
        await member.add_roles(role)
        channel = bot.get_channel(CHANNEL_ID)
        await channel.send(f"Congratulations to {member.mention} for becoming the new Champion of the Server!")


def givePoints():
    return int(max_points * (1 - math.log1p((time.time() - start_time) / duration * 9) / math.log1p(9)))
    #return int(max(max_points - (int(time.time() - start_time))**points_scaler, 0))

@tasks.loop(seconds=.1)
async def logScore():
    if challenge != "None":
        print(f"time: {(time.time() - start_time)}, score: {givePoints()}")

@tasks.loop(seconds=duration)
async def check_challenge_time():
    global challenge
    if challenge != "None" and time.time() - start_time >= duration:
        challenge = "None"
        channel = bot.get_channel(CHANNEL_ID)
        await channel.send("The challenge time has ended!")

@tasks.loop(hours=24)
async def check_monthly_champion():
    if datetime.now().day == 1 and lb: awardChampion()

async def force_champion():
    if lb: awardChampion()

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    await run_challenge()
    check_challenge_time.start()
    check_monthly_champion.start()
    #logScore.start()


@bot.command()
async def leaderboard(ctx):
    embed = discord.Embed(title="Leaderboard", color=0xffd700)
    for idx, (uid, pts) in enumerate(sorted(lb.items(), key=lambda x: x[1], reverse=True), start=1):
        member = await bot.fetch_user(uid)
        embed.add_field(name="\u200b", value=f"{idx}) {member.display_name} - ({pts} points)", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def mondo_help(ctx):
    embed = discord.Embed(title="Bot Commands", description="List of available commands", color=0x00ff00)
    embed.add_field(name="m!leaderboard", value="View the leaderboard", inline=False)
    embed.add_field(name="m!chal", value="Start a challenge", inline=False)
    embed.add_field(name="m!end", value="End a challenge", inline=False)
    embed.add_field(name="m!back", value="Respond to a 'Back' challenge", inline=False)
    embed.add_field(name="m!over", value="Respond to an 'Over' challenge", inline=False)
    embed.add_field(name="notes", value="Challenges run 10am-10pm. Answering late gives 2x points.", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def champ(ctx):
    await force_champion()

@bot.command()
async def chal(ctx):
    await run_challenge()

@bot.command()
async def end(ctx):
    global challenge
    if challenge != "None":
        challenge = "None"
        await ctx.send("Challenge ended")

@bot.command()
async def back(ctx):
    await handle_challenge_response(ctx, "Back")

@bot.command()
async def over(ctx):
    await handle_challenge_response(ctx, "Over")

async def handle_challenge_response(ctx, expected):
    global challenge
    if challenge != expected:
        await ctx.send("No active challenge or wrong type.")
        return
    uid = ctx.author.id
    if uid in answered_incorrectly:
        await ctx.send(f"{ctx.author.mention} You already answered incorrectly!")
        return
    points = givePoints() * 2 if uid in answered_correctly else givePoints()
    update_leaderboard(uid, points)
    await ctx.send(f"{ctx.author.mention} You gained {points} points! Total: {lb[uid]}")
    answered_correctly.add(uid)
    challenge = "None"

@bot.event
async def on_message(message):
    await bot.process_commands(message)
    if message.content.startswith("m!"):
        return
    if challenge != "None" and message.content.startswith("m!") and message.author.id not in answered_correctly:
        if message.author.id not in answered_incorrectly:
            answered_incorrectly.add(message.author.id)
            await message.channel.send(f"{message.author.mention} Incorrect! Other players now get 2X points.")

async def run_challenge():
    global challenge, start_time
    await bot.wait_until_ready()
    channel = bot.get_channel(CHANNEL_ID)
    challenge = random.choice(["Back", "Over"])
    file_path = f"images/{challenge.lower()}.png"
    embed = discord.Embed(title=f"Are we {challenge.lower()}?", color=discord.Color.red())
    with open(file_path, "rb") as f:
        file = discord.File(f, filename="image.png")
    embed.set_image(url="attachment://image.png")
    await channel.send(file=file, embed=embed)
    start_time = time.time()
    answered_correctly.clear()
    answered_incorrectly.clear()


load_leaderboard(LEADERBOARD_FILE) ## Initializes the leaderboard if bot restarts
bot.run(secret_token)