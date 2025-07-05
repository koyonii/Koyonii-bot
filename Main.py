import discord
from discord.ext import commands, tasks
import json
import os
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

xp_file = "xp_data.json"
eco_file = "eco_data.json"
cooldowns = {}

WELCOME_CHANNEL_NAME = "welcome"

# --------------- Helper Functions ---------------

def load_json(file):
    if os.path.exists(file):
        with open(file, "r") as f:
            return json.load(f)
    return {}

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)

def add_xp(user_id, amount):
    data = load_json(xp_file)
    uid = str(user_id)
    if uid not in data:
        data[uid] = {"xp": 0, "level": 1}
    data[uid]["xp"] += amount
    level = data[uid]["level"]
    needed = 100 * level
    if data[uid]["xp"] >= needed:
        data[uid]["xp"] -= needed
        data[uid]["level"] += 1
        save_json(xp_file, data)
        return True, data[uid]["level"]
    save_json(xp_file, data)
    return False, None

def get_balance(user_id):
    data = load_json(eco_file)
    uid = str(user_id)
    if uid not in data:
        data[uid] = {"balance": 0, "last_work": None, "last_daily": None}
        save_json(eco_file, data)
    return data[uid]["balance"]

def update_balance(user_id, amount):
    data = load_json(eco_file)
    uid = str(user_id)
    if uid not in data:
        data[uid] = {"balance": 0, "last_work": None, "last_daily": None}
    data[uid]["balance"] += amount
    save_json(eco_file, data)

# --------------- Bot Events ---------------

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="✨ Serving Kawaii Vibes ✨"))
    print(f"Logged in as {bot.user}!")

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    leveled_up, level = add_xp(message.author.id, 10)
    if leveled_up:
        await message.channel.send(f"🌸 {message.author.mention} leveled up to **Level {level}**!! ✨")
    await bot.process_commands(message)

@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name=WELCOME_CHANNEL_NAME)
    if channel:
        await channel.send(f"🎀 Welcome to the server, {member.mention}! You're officially a cutie now 💖")

# --------------- Commands ---------------

@bot.command()
async def rank(ctx):
    data = load_json(xp_file)
    uid = str(ctx.author.id)
    if uid in data:
        level = data[uid]["level"]
        xp = data[uid]["xp"]
        embed = discord.Embed(
            title=f"💫 {ctx.author.name}'s Rank",
            description=f"🌸 Level: **{level}**\n✨ XP: **{xp}/{100 * level}**",
            color=discord.Color.pink()
        )
        await ctx.send(embed=embed)
    else:
        await ctx.send("Start chatting to earn XP cutie~!")

@bot.command()
async def bownick(ctx):
    try:
        new_nick = f"🎀 {ctx.author.name} 🎀"
        await ctx.author.edit(nick=new_nick)
        await ctx.send(f"Now your name is extra adorable 💕: `{new_nick}`")
    except:
        await ctx.send("I can't change your nickname 😭")

@bot.command()
async def balance(ctx):
    bal = get_balance(ctx.author.id)
    await ctx.send(f"🍰 You have **{bal} cupcakes**!")

@bot.command()
async def work(ctx):
    uid = str(ctx.author.id)
    data = load_json(eco_file)
    now = datetime.now()
    last_work = data.get(uid, {}).get("last_work")
    if last_work:
        then = datetime.fromisoformat(last_work)
        if now - then < timedelta(seconds=60):
            await ctx.send("⏳ Slow down cutie! You can work again in 1 min!")
            return
    earned = random.randint(10, 40)
    update_balance(ctx.author.id, earned)
    data[uid]["last_work"] = now.isoformat()
    save_json(eco_file, data)
    await ctx.send(f"💼 You worked hard and earned **{earned} cupcakes**!")

@bot.command()
async def daily(ctx):
    uid = str(ctx.author.id)
    data = load_json(eco_file)
    now = datetime.now()
    last = data.get(uid, {}).get("last_daily")
    if last:
        then = datetime.fromisoformat(last)
        if now - then < timedelta(hours=24):
            await ctx.send("🕒 Come back tomorrow for your daily reward!")
            return
    reward = 100
    update_balance(ctx.author.id, reward)
    data[uid]["last_daily"] = now.isoformat()
    save_json(eco_file, data)
    await ctx.send(f"🎁 You claimed your daily reward: **{reward} cupcakes**!")

@bot.command()
async def hug(ctx, member: discord.Member):
    gifs = [
        "https://media.tenor.com/7C2tD1lE9cwAAAAC/anime-hug.gif",
        "https://media.tenor.com/Zv-B3O2ojxwAAAAC/aharen-hug.gif"
    ]
    embed = discord.Embed(description=f"💞 {ctx.author.mention} hugs {member.mention}!", color=0xffc0cb)
    embed.set_image(url=random.choice(gifs))
    await ctx.send(embed=embed)

@bot.command()
async def pat(ctx, member: discord.Member):
    gifs = [
        "https://media.tenor.com/2rI7HAgDhnwAAAAC/anime-pat.gif",
        "https://media.tenor.com/ZsrC61GqZk8AAAAC/head-pat.gif"
    ]
    embed = discord.Embed(description=f"✨ {ctx.author.mention} pats {member.mention} gently!", color=0xffc0cb)
    embed.set_image(url=random.choice(gifs))
    await ctx.send(embed=embed)

# --- Moderation Commands ---
@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="No reason"):
    await member.kick(reason=reason)
    await ctx.send(f"👢 {member.mention} has been kicked. Byeee~!")

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="No reason"):
    await member.ban(reason=reason)
    await ctx.send(f"🔨 {member.mention} has been banned. Banned with love 💔")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def purge(ctx, amount: int):
    await ctx.channel.purge(limit=amount+1)
    await ctx.send(f"🧹 Cleaned up {amount} messages!", delete_after=3)

bot.run(TOKEN)
