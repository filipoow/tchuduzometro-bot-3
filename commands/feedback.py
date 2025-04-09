import discord
from discord.ext import commands
from discord import app_commands
from utils.embeds import embed_sucesso

class Feedback(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ajuda", description="Veja os comandos disponíveis e o que eles fazem")
    async def ajuda(self, interaction: discord.Interaction):
        texto = (
            "🔧 **Comandos disponíveis:**\n"
            "• /choquederealidade — Dá um choque em alguém\n"
            "• /passou — Acusa alguém de se passar\n"
            "• /ranking — Exibe o ranking de tempo em call\n"
            "• /level — Mostra seu XP e progresso\n"
            "• /ajuda — Lista de comandos\n\n"
            "✅ Resumos, enquetes e premiações são automáticos."
        )
        await interaction.response.send_message(embed=embed_sucesso(texto))

async def setup(bot):
    await bot.add_cog(Feedback(bot))
