import discord
from discord.ext import commands
from discord import app_commands
from db import fetchall, execute
from datetime import datetime, timedelta

class Premiacao(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="premiacao", description="Executa manualmente a premiação mensal")
    @app_commands.checks.has_permissions(administrator=True)
    async def premiacao(self, interaction: discord.Interaction):
        now = datetime.utcnow()
        guild_id = interaction.guild.id

        conf = fetchall("SELECT canal_configurado, cargo_designado FROM configuracoes WHERE guild_id = %s", (guild_id,))
        if not conf:
            await interaction.response.send_message("Configuração não encontrada.", ephemeral=True)
            return

        canal_id, cargo_id = conf[0]
        resultado = fetchall("""
            SELECT usuario_id, usuario_nome, SUM(tempo_sessao) as total
            FROM sessoes_voz
            WHERE guild_id = %s AND entrada >= %s
            GROUP BY usuario_id, usuario_nome
            ORDER BY total ASC LIMIT 1
        """, (guild_id, now.replace(day=1) - timedelta(days=1)))

        if not resultado:
            await interaction.response.send_message("Nenhum dado para premiar.", ephemeral=True)
            return

        usuario_id, nome, tempo_total = resultado[0]
        canal = interaction.guild.get_channel(canal_id)
        membro = interaction.guild.get_member(usuario_id)
        cargo = interaction.guild.get_role(cargo_id)
        if membro and cargo:
            await membro.add_roles(cargo)

        embed = discord.Embed(
            title="💩 Tchudu Bem Master do Mês",
            description="Menor participação em chamadas de voz.",
            color=discord.Color.dark_gray()
        )
        embed.set_image(url="https://media.giphy.com/media/xUA7bdpLxQhsSQdyog/giphy.gif")
        embed.add_field(name="Nome do sumido", value=f"<@{usuario_id}>", inline=True)
        embed.add_field(name="Tempo total", value=str(tempo_total).split('.')[0], inline=True)
        embed.add_field(name="Ranking de engajamento", value="Último lugar", inline=True)
        embed.set_footer(text="Parabéns pela insignificância digital.")
        embed.timestamp = now
        await canal.send(embed=embed)

        execute("INSERT INTO logs (timestamp, tipo_evento, descricao, funcionalidade, usuario_id) VALUES (%s,%s,%s,%s,%s)",
                (now, 'Premiação', f"Tchudu Bem Master: {usuario_id}", '/premiacao', usuario_id), commit=True)

async def setup(bot):
    await bot.add_cog(Premiacao(bot))