import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from response import build_odds_response

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}!")

@bot.command()
async def odds(ctx, *, teams: str):
    response = await build_odds_response(teams)
    await ctx.send(response)

bot.run(DISCORD_TOKEN)
