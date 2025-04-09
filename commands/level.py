import discord
from discord.ext import commands
from discord import app_commands
from db import fetchall
from datetime import timedelta

class Level(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="level", description="Veja seu nível atual e XP")
    async def level(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        guild_id = interaction.guild.id

        config = fetchall("SELECT tempo_para_xp, xp_por_intervalo, coeficiente_progresso FROM configuracoes WHERE guild_id = %s", (guild_id,))
        if not config:
            await interaction.response.send_message("⚠️ Configuração não encontrada para este servidor.", ephemeral=True)
            return

        tempo_para_xp, xp_por_intervalo, coef = config[0]

        result = fetchall("""
            SELECT SUM(tempo_sessao), SUM(xp_ganho), MAX(xp_total), MAX(nivel)
            FROM sessoes_voz
            WHERE usuario_id = %s AND guild_id = %s
        """, (user_id, guild_id))

        total_tempo, xp_ganho, xp_total, nivel = result[0]
        if not total_tempo:
            await interaction.response.send_message("Você ainda não tem participação registrada em chamadas de voz.", ephemeral=True)
            return

        proximo_xp = int(xp_por_intervalo * ((coef) ** (nivel or 1)))
        progresso = int((xp_total or 0) / proximo_xp * 5)
        barra = '▰' * progresso + '▱' * (5 - progresso)

        embed = discord.Embed(
            title="📈 Seu Nível",
            color=discord.Color.purple()
        )
        embed.set_thumbnail(url=interaction.user.avatar.url if interaction.user.avatar else discord.Embed.Empty)
        embed.add_field(name="XP Atual", value=f"{xp_total or 0}", inline=True)
        embed.add_field(name="Nível", value=f"{nivel or 0}", inline=True)
        embed.add_field(name="XP p/ próximo nível", value=f"{proximo_xp}", inline=True)
        embed.add_field(name="Tempo total em call", value=str(total_tempo).split('.')[0], inline=False)
        embed.add_field(name="Progresso", value=barra, inline=False)
        embed.timestamp = interaction.created_at

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Level(bot))
