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
@commands.cooldown(4, 60, commands.BucketType.user)  # 3 uses per 60s per user
async def odds(ctx, *, teams: str):
    response = await build_odds_response(teams)
    await ctx.send(response)

@odds.error
async def odds_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"⏳ Whoa there! Try again in {round(error.retry_after)}s.")

bot.run(DISCORD_TOKEN)
