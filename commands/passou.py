import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timedelta
from db import execute

class Passou(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="passou", description="Acusa alguém de se passar demais")
    @app_commands.describe(usuario="Usuário acusado de se passar")
    async def passou(self, interaction: discord.Interaction, usuario: discord.Member):
        now = datetime.utcnow()
        canal = interaction.channel

        # Cria embed
        embed = discord.Embed(
            title="🧨 Julgamento: Acusação de 'Se Passar'",
            description=f"{interaction.user.mention} está acusando {usuario.mention} de SE PASSAR DEMAIS!",
            color=discord.Color.orange()
        )
        embed.set_image(url="https://media.giphy.com/media/3o6Zt6ML6BklcajjsA/giphy.gif")
        embed.add_field(name="Acusador", value=interaction.user.display_name, inline=True)
        embed.add_field(name="Acusado", value=usuario.display_name, inline=True)
        embed.add_field(name="Votação ativa por", value="3 minutos", inline=False)
        embed.set_footer(text="Seu voto será registrado. Justiça será feita… talvez.")
        embed.timestamp = now

        # Envia embed com botões
        class Votacao(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=180)
                self.votos = {"Sim": 0, "Não": 0, "Condenar": 0}
                self.votantes = []

            @discord.ui.button(label="SIM", style=discord.ButtonStyle.success)
            async def sim(self, interaction_btn: discord.Interaction, _):
                await self.registrar_voto(interaction_btn, "Sim")

            @discord.ui.button(label="NÃO", style=discord.ButtonStyle.danger)
            async def nao(self, interaction_btn: discord.Interaction, _):
                await self.registrar_voto(interaction_btn, "Não")

            @discord.ui.button(label="CONDENAR", style=discord.ButtonStyle.secondary)
            async def condenar(self, interaction_btn: discord.Interaction, _):
                await self.registrar_voto(interaction_btn, "Condenar")

            async def registrar_voto(self, interaction_btn, opcao):
                if interaction_btn.user.id in self.votantes:
                    await interaction_btn.response.send_message("Você já votou.", ephemeral=True)
                    return
                self.votantes.append(interaction_btn.user.id)
                self.votos[opcao] += 1
                execute("INSERT INTO votos_passou (votacao_id, votante_id, timestamp, opcao) VALUES (%s,%s,%s,%s)", (
                    self.votacao_id, interaction_btn.user.id, datetime.utcnow(), opcao
                ), commit=True)
                await interaction_btn.response.send_message(f"Voto '{opcao}' registrado!", ephemeral=True)

        view = Votacao()

        # Registro inicial da votação
        execute("""
            INSERT INTO votacoes_passou (guild_id, canal_id, inicio, fim, acusador_id, acusador_nome, acusado_id, acusado_nome, votos_sim, votos_nao, votos_condenar, resultado_final, lista_votantes, data_finalizacao)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,0,0,0,NULL,ARRAY[]::TEXT[],NULL)
        """, (
            interaction.guild.id, canal.id, now, now + timedelta(minutes=3),
            interaction.user.id, interaction.user.display_name,
            usuario.id, usuario.display_name
        ), commit=True)

        votacao_id = execute("SELECT MAX(votacao_id) FROM votacoes_passou")[0][0]
        view.votacao_id = votacao_id

        await interaction.response.send_message(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Passou(bot))
