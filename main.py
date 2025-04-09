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
    print("📦 Tabelas do banco verificadas/criadas com segurança.")

    extensoes = [
        "commands.configurar",
        "commands.choquederealidade",
        "commands.passou",
        "commands.ranking",
        "commands.level",
        "commands.resumo",
        "commands.enquete",
        "commands.premiacao",
        "commands.feedback",
        "commands.admin_alerta",
        "listeners.voice_tracking"
    ]

    for ext in extensoes:
        try:
            await bot.load_extension(ext)
            print(f"✅ Módulo carregado: {ext}")
        except Exception as e:
            print(f"❌ Erro ao carregar {ext}: {e}")

    setup_scheduler(bot)

bot.run(os.getenv("TOKEN"))