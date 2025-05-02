import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timedelta
from db import execute

class Passou(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="passou",
        description="Acusa alguém de se passar demais"
    )
    @app_commands.describe(
        usuario="Usuário acusado de se passar"
    )
    async def passou(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member
    ):
        now = datetime.utcnow()
        canal = interaction.channel

        # 1) Monta o embed de início de votação
        embed = discord.Embed(
            title="🧨 Julgamento: Acusação de 'Se Passar'",
            description=f"{interaction.user.mention} acusa {usuario.mention} de se passar demais!",
            color=discord.Color.orange(),
            timestamp=now
        )
        embed.set_image(
            url="https://media.giphy.com/media/3o6Zt6ML6BklcajjsA/giphy.gif"
        )
        embed.add_field(
            name="Acusador", value=interaction.user.display_name, inline=True
        )
        embed.add_field(
            name="Acusado", value=usuario.display_name, inline=True
        )
        embed.add_field(
            name="Votação ativa por", value="3 minutos", inline=False
        )
        embed.set_footer(
            text="Seu voto será registrado. Justiça será feita… talvez."
        )

        # 2) Define a UI para os botões
        class VotacaoView(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=180)
                self.votacao_id: int | None = None
                self.votantes: set[int] = set()
                self.votos = {"Sim": 0, "Não": 0, "Condenar": 0}

            async def _registra(self, interaction_btn: discord.Interaction, opcao: str):
                # evita voto duplo
                if interaction_btn.user.id in self.votantes:
                    await interaction_btn.response.send_message(
                        "Você já votou.", ephemeral=True
                    )
                    return
                self.votantes.add(interaction_btn.user.id)
                self.votos[opcao] += 1

                # Insere na tabela votos_passou
                execute(
                    """
                    INSERT INTO votos_passou
                        (votacao_id, votante_id, timestamp, opcao)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (
                        self.votacao_id,
                        interaction_btn.user.id,
                        datetime.utcnow(),
                        opcao
                    ),
                    commit=True
                )

                await interaction_btn.response.send_message(
                    f"Voto '{opcao}' registrado!", ephemeral=True
                )

            @discord.ui.button(label="SIM", style=discord.ButtonStyle.success)
            async def sim(self, interaction_btn, button):
                await self._registra(interaction_btn, "Sim")

            @discord.ui.button(label="NÃO", style=discord.ButtonStyle.danger)
            async def nao(self, interaction_btn, button):
                await self._registra(interaction_btn, "Não")

            @discord.ui.button(label="CONDENAR", style=discord.ButtonStyle.secondary)
            async def condenar(self, interaction_btn, button):
                await self._registra(interaction_btn, "Condenar")

        view = VotacaoView()

        # 3) Insere em votacoes_passou e já recupera o votacao_id gerado
        rows = execute(
            """
            INSERT INTO votacoes_passou
                (guild_id, canal_id, inicio, fim,
                 acusador_id, acusador_nome,
                 acusado_id, acusado_nome,
                 votos_sim, votos_nao, votos_condenar,
                 resultado_final, lista_votantes, data_finalizacao)
            VALUES
                (%s, %s, %s, %s,
                 %s, %s,
                 %s, %s,
                 0, 0, 0,
                 NULL, ARRAY[]::TEXT[], NULL)
            RETURNING votacao_id
            """,
            (
                interaction.guild.id,
                canal.id,
                now,
                now + timedelta(minutes=3),
                interaction.user.id,
                interaction.user.display_name,
                usuario.id,
                usuario.display_name,
            ),
            commit=True
        )

        # 4) Ajusta view.votacao_id com o resultado do RETURNING
        if rows and rows[0] and rows[0][0] is not None:
            view.votacao_id = rows[0][0]
        else:
            # fallback seguro
            sel = execute("SELECT MAX(votacao_id) FROM votacoes_passou")
            view.votacao_id = sel[0][0] if sel and sel[0] else 1

        # 5) Envia a mensagem com os botões
        await interaction.response.send_message(embed=embed, view=view)


async def setup(bot: commands.Bot):
    await bot.add_cog(Passou(bot))