import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timedelta
from db import fetchall

class Resumo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="resumo", description="Gera o resumo diário manualmente")
    @app_commands.checks.has_permissions(administrator=True)
    async def resumo(self, interaction: discord.Interaction):
        now = datetime.utcnow()
        guild_id = interaction.guild.id

        resumo = fetchall("""
            SELECT usuario_nome, SUM(tempo_sessao) as total
            FROM sessoes_voz
            WHERE guild_id = %s AND entrada::date = %s
            GROUP BY usuario_nome ORDER BY total DESC
        """, (guild_id, now.date()))

        if not resumo:
            await interaction.response.send_message("Nenhum dado registrado hoje.", ephemeral=True)
            return

        mais_ativo = resumo[0][0]
        longas = [r for r in resumo if r[1] and r[1].total_seconds() > 3600]
        medias = sum(r[1].total_seconds() for r in resumo) / len(resumo)
        medias = str(timedelta(seconds=int(medias)))

        embed = discord.Embed(
            title="📊 Resumo Diário",
            color=discord.Color.dark_blue()
        )
        embed.add_field(name="Sessões com +1h", value=str(len(longas)), inline=True)
        embed.add_field(name="Média por sessão", value=medias, inline=True)
        embed.add_field(name="Mais ativo", value=mais_ativo, inline=True)
        embed.set_footer(text="Boa noite, e continue firme amanhã!")
        embed.timestamp = now

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Resumo(bot))