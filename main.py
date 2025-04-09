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
        "listeners.voice_tracking",
        "listeners.enquete_listener"
    ]

    for ext in extensoes:
        try:
            await bot.load_extension(ext)
            print(f"✅ Módulo carregado: {ext}")
        except Exception as e:
            print(f"❌ Erro ao carregar {ext}: {e}")

    setup_scheduler(bot)

    try:
        synced = await bot.tree.sync()
        print(f"✅ Comandos sincronizados globalmente: {len(synced)}")
    except Exception as e:
        print(f"❌ Erro ao sincronizar comandos: {e}")

@bot.event
async def on_guild_join(guild):
    try:
        synced = await bot.tree.sync(guild=guild)
        print(f"🔁 Comandos sincronizados com a guilda {guild.name} ({guild.id})")
    except Exception as e:
        print(f"❌ Erro ao sincronizar comandos na guilda {guild.id}: {e}")

bot.run(os.getenv("TOKEN"))