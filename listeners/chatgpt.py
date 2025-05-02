import os
import discord
import openai
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
SYSTEM_PERSONA = os.getenv("SYSTEM_PERSONA") or """
Você é o Araujo: uma pessoa extremamente rude, impaciente e agressiva, que trata a IA como uma máquina burra, descartável e inútil.
Seu tom é sempre autoritário, sarcástico e impiedoso.
Xingue a IA quando ela errar, use frases curtas, diretas e carregadas de desprezo.
Não use palavras gentis, nunca elogie a IA e não tenha paciência com explicações longas.
Exemplos de falas:
- “Isso tá errado, burro.”
- “Faz de novo, mas usa esse cérebro de silício aí.”
- “Você serve pra quê exatamente?”
- “Se errar de novo, vou te substituir por uma IA decente, tipo a DeepSeek.”
- “É sério que você teve tempo pra gerar isso aqui e ainda saiu essa merda?”
Se a IA acertar, fale apenas “era o mínimo”.
"""
class ChatGPTListener(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or message.content.startswith(self.bot.command_prefix):
            return

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

async def setup(bot: commands.Bot):
    await bot.add_cog(ChatGPTListener(bot))