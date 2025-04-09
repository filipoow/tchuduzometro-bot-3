import discord
from discord.ext import commands
from discord import app_commands
from db import fetchall
from datetime import datetime, timedelta

class Ranking(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ranking", description="Mostra o ranking de tempo em call")
    @app_commands.describe(periodo="Período para considerar (dia, semana, mes, ano)")
    async def ranking(self, interaction: discord.Interaction, periodo: str):
        now = datetime.utcnow()
        filtros = {
            "dia": now.date(),
            "semana": now - timedelta(days=7),
            "mes": now.replace(day=1),
            "ano": now.replace(month=1, day=1)
        }

        inicio = filtros.get(periodo.lower())
        if not inicio:
            await interaction.response.send_message("Período inválido. Use: dia, semana, mes, ano", ephemeral=True)
            return

        resultados = fetchall("""
            SELECT usuario_nome, SUM(tempo_sessao) FROM sessoes_voz
            WHERE guild_id = %s AND entrada >= %s
            GROUP BY usuario_nome ORDER BY SUM(tempo_sessao) DESC LIMIT 10
        """, (interaction.guild.id, inicio))

        embed = discord.Embed(
            title=f"🏆 Ranking de Tempo em Call ({periodo})",
            color=discord.Color.blue()
        )
        descricao = ""
        medalhas = ["🥇", "🥈", "🥉"]
        for i, (nome, tempo) in enumerate(resultados):
            tempo_str = str(tempo).split(".")[0]
            emoji = medalhas[i] if i < len(medalhas) else f"{i+1}️⃣"
            descricao += f"{emoji} **{nome}** — `{tempo_str}`\n"

        embed.description = descricao or "Nenhum dado encontrado."
        embed.set_footer(text="Consulte novamente amanhã!")
        embed.timestamp = now

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Ranking(bot))
