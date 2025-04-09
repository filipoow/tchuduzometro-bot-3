import discord
from discord.ext import commands
from discord import app_commands
from utils.embeds import embed_alerta
from db import execute
from datetime import datetime

class AdminAlerta(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="alerta_admin", description="Envia um alerta manual para o canal de admins")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(tipo="Tipo do alerta", descricao="Descrição detalhada", funcao="Função afetada")
    async def alerta_admin(self, interaction: discord.Interaction, tipo: str, descricao: str, funcao: str):
        embed = embed_alerta(tipo, descricao, funcao)
        await interaction.response.send_message(embed=embed)

        execute("INSERT INTO logs (timestamp, tipo_evento, descricao, funcionalidade, usuario_id) VALUES (%s,%s,%s,%s,%s)",
                (datetime.utcnow(), tipo, descricao, funcao, interaction.user.id), commit=True)

async def setup(bot):
    await bot.add_cog(AdminAlerta(bot))
