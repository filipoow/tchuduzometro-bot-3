import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
from db import execute

OPCOES = {
    "🟨": "EITCHAAAAAA",
    "🔵": "OPA...",
    "🟢": "TCHUDU BEM",
    "🔴": "FUI BUSCAR O CRACHÁ"
}

class Enquete(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="enquete", description="Envia a enquete diária manualmente")
    @app_commands.checks.has_permissions(administrator=True)
    async def enquete(self, interaction: discord.Interaction):
        now = datetime.utcnow()
        embed = discord.Embed(
            title="📢 Hoje é 'EITCHA' ou 'TCHUDU BEM'?",
            description="Vote abaixo e registre sua presença! 🎧\n\n"
                        "🟨 **EITCHAAAAAA**\n🔥 Fiquei mais de 1h!\n\n"
                        "🔵 **OPA...**\n👀 Ainda não sei...\n\n"
                        "🟢 **TCHUDU BEM....**\n💤 Passei menos de 1h na call...\n\n"
                        "🔴 **FUI BUSCAR O CRACHÁ**\n📛 Não participei hoje.",
            color=discord.Color.yellow()
        )
        embed.set_footer(text="Vote antes da meia-noite!")
        embed.timestamp = now

        await interaction.response.send_message(embed=embed)
        msg = await interaction.original_response()

        for emoji in OPCOES:
            await msg.add_reaction(emoji)

        execute("INSERT INTO interacoes (timestamp, comando, guild_id, canal_id, usuario_id, nome_usuario, parametros, resultado) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                (now, "/enquete", interaction.guild.id, interaction.channel.id, interaction.user.id, interaction.user.display_name, "manual", "enquete enviada"),
                commit=True)

        # Salvar ID da mensagem de enquete para o listener
        self.bot.enquete_msg_id = msg.id
        self.bot.enquete_user_votos = {}

async def setup(bot):
    await bot.add_cog(Enquete(bot))
