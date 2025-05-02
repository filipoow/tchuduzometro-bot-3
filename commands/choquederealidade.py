import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
from db import execute, fetchall

class Choque(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="choquederealidade", description="Dá um choque de realidade em outro usuário")
    @app_commands.describe(usuario="Usuário que receberá o choque")
    async def choque(self, interaction: discord.Interaction, usuario: discord.Member):
        now = datetime.utcnow()
        giver = interaction.user
        receiver = usuario

        # Registra no banco
        execute("""
            INSERT INTO choques (timestamp, giver_id, giver_nome, receiver_id, receiver_nome, choques_dados, choques_recebidos, observacoes)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            now, giver.id, giver.display_name, receiver.id, receiver.display_name, 1, 1, None
        ), commit=True)

        # Busca contagem de choques entre esses usuários
        choques_dados = fetchall("""
            SELECT COUNT(*) FROM choques
            WHERE giver_id = %s AND receiver_id = %s
        """, (giver.id, receiver.id))[0][0]

        choques_recebidos = fetchall("""
            SELECT COUNT(*) FROM choques
            WHERE receiver_id = %s AND giver_id = %s
        """, (receiver.id, giver.id))[0][0]

        # Criação do embed
        embed = discord.Embed(
            title="⚡ Choque de Realidade!",
            description=f"{giver.mention} deu um choque de realidade em {receiver.mention}!",
            color=discord.Color.gold()
        )
        embed.set_image(url="https://i.gifer.com/1IYp.gif")
        embed.add_field(name="Quem deu o choque", value=giver.display_name, inline=True)
        embed.add_field(name="Quem recebeu", value=receiver.display_name, inline=True)
        embed.add_field(name="Total de choques dados para esse usuário", value=str(choques_dados), inline=False)
        embed.add_field(name="Total de choques recebidos por esse usuário", value=str(choques_recebidos), inline=False)
        embed.set_footer(text="Use com moderação... ou não 👀")
        embed.timestamp = now

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Choque(bot))