import os
import discord
import openai
from discord.ext import commands
from config import OPENAI_API_KEY, SYSTEM_PERSONA

openai.api_key = OPENAI_API_KEY

class ChatGPTListener(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Ignora bots e comandos slash
        if message.author.bot or message.content.startswith(self.bot.command_prefix):
            return

        # Só reage se for menção direta
        if self.bot.user in message.mentions:
            prompt = message.content.replace(f"<@!{self.bot.user.id}>", "").strip()
            async with message.channel.typing():
                try:
                    resp = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": SYSTEM_PERSONA},
                            {"role": "user",   "content": prompt}
                        ],
                        max_tokens=150,
                        temperature=0.7
                    )
                    reply = resp.choices[0].message.content.strip()
                except Exception:
                    reply = "Erro de API, seu silício inútil."

            await message.reply(reply, mention_author=True)

def setup(bot: commands.Bot):
    bot.add_cog(ChatGPTListener(bot))