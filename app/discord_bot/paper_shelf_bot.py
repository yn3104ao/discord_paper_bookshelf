import os
import discord
from discord.ext import commands, tasks

from dotenv import load_dotenv

# import environment variable
load_dotenv()

# discord bot settings
intents = discord.Intents.default()
intents.typing = False
intents.presences = False

bot = commands.Bot(command_prefix="!", intents=intents)

# 起動時に実行されるイベントハンドラ
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

# メッセージ受信時に実行されるイベントハンドラ
@bot.event
async def on_message(message):
    if message.author.bot:
        return
    # 「要約して」と投稿したら"summarize_util"を実行
    if message.content is "要約して":
        pass

# リアクション追加時に実行されるイベントハンドラ
@bot.event
async def on_reaction_add(reaction, user):
    # summarize_utilを非同期で呼び出す
    pass

# slash command example
@bot.slash_command()
async def hello(ctx):
    await ctx.send("Hello, world!")

# Botトークンを貼り付けてください
bot.run(os.environ.get("DISCORD_API_TOKEN"))
