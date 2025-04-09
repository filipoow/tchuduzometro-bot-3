import discord
from discord.ext import commands

class EnqueteListener(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        # Confere se é a mensagem da enquete
        if not hasattr(self.bot, "enquete_msg_id"):
            return

        if payload.message_id != self.bot.enquete_msg_id:
            return

        guild = self.bot.get_guild(payload.guild_id)
        channel = guild.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        member = guild.get_member(payload.user_id)

        if member.bot:
            return

        # Remove qualquer outra reação do mesmo usuário
        for reaction in message.reactions:
            users = await reaction.users().flatten()
            if reaction.emoji != payload.emoji.name and member in users:
                await message.remove_reaction(reaction.emoji, member)

async def setup(bot):
    await bot.add_cog(EnqueteListener(bot))
