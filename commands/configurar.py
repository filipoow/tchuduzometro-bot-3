import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
from db import execute

def log_uso(timestamp, comando, usuario_id, parametros, feedback):
    execute(
        "INSERT INTO uso (timestamp, comando, usuario_id, parametros, feedback) VALUES (%s,%s,%s,%s,%s)",
        (timestamp, comando, usuario_id, parametros, feedback),
        commit=True
    )

class Configurar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="configurar", description="Define as configurações do servidor para o bot")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(
        canal_configurado="Canal onde serão enviados enquetes e resumos",
        cargo_designado="Cargo usado para premiação mensal",
        tempo_para_xp="Minutos para ganhar XP",
        xp_por_intervalo="XP ganho por intervalo",
        coeficiente_progresso="Coeficiente de progressão do XP"
    )
    async def configurar(self,
        interaction: discord.Interaction,
        canal_configurado: discord.TextChannel,
        cargo_designado: discord.Role,
        tempo_para_xp: int,
        xp_por_intervalo: int,
        coeficiente_progresso: float
    ):
        now = datetime.utcnow()
        execute(
            """
            INSERT INTO configuracoes (guild_id, nome_servidor, canal_configurado, cargo_designado, tempo_para_xp, xp_por_intervalo, coeficiente_progresso, data_configuracao)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (guild_id) DO UPDATE SET
                nome_servidor = EXCLUDED.nome_servidor,
                canal_configurado = EXCLUDED.canal_configurado,
                cargo_designado = EXCLUDED.cargo_designado,
                tempo_para_xp = EXCLUDED.tempo_para_xp,
                xp_por_intervalo = EXCLUDED.xp_por_intervalo,
                coeficiente_progresso = EXCLUDED.coeficiente_progresso,
                data_configuracao = EXCLUDED.data_configuracao
            """,
            (
                interaction.guild.id,
                interaction.guild.name,
                canal_configurado.id,
                cargo_designado.id,
                tempo_para_xp,
                xp_por_intervalo,
                coeficiente_progresso,
                now
            ),
            commit=True
        )

        log_uso(
            now,
            "/configurar",
            interaction.user.id,
            f"canal={canal_configurado.id}, cargo={cargo_designado.id}, tempo={tempo_para_xp}, xp={xp_por_intervalo}, coef={coeficiente_progresso}",
            "Configuração aplicada com sucesso."
        )

        embed = discord.Embed(
            title="⚙️ Configuração Aplicada",
            description="As configurações do servidor foram salvas com sucesso!",
            color=discord.Color.green()
        )
        embed.add_field(name="Canal Configurado", value=canal_configurado.mention)
        embed.add_field(name="Cargo Designado", value=cargo_designado.mention)
        embed.add_field(name="Tempo p/ XP", value=f"{tempo_para_xp} min")
        embed.add_field(name="XP por Intervalo", value=f"{xp_por_intervalo}")
        embed.add_field(name="Coeficiente de Progressão", value=str(coeficiente_progresso))
        embed.timestamp = now
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Configurar(bot))