# Arquivo: README.md

import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from db import execute
from models import SCHEMA_SETUP
from scheduler.tasks import setup_scheduler

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True

bot = commands.Bot(command_prefix="/", intents=intents)

@bot.event
async def on_ready():
    print(f"🤖 Bot conectado como {bot.user}")
    execute(SCHEMA_SETUP, commit=True)
  ...
