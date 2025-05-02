import os
import discord
from discord.ext import commands
from openai import OpenAI
from dotenv import load_dotenv

# Carrega .env
load_dotenv()

# Instancia o client do OpenAI (ou DeepSeek, etc.)
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
)

# Define a persona do Araujo (pode vir do .env ou ficar hardcoded)
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
        # Ignora mensagens de bots e comandos slash
        if message.author.bot or message.content.startswith(self.bot.command_prefix):
            return

        # Verifica menção ao bot
        if self.bot.user in message.mentions:
            # Remove a menção do conteúdo
            prompt = message.content.replace(f"<@!{self.bot.user.id}>", "").strip()
            async with message.channel.typing():
                try:
                    # Chama a API com o novo client
                    resp = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": SYSTEM_PERSONA},
                            {"role": "user",   "content": prompt}
                        ],
                        max_tokens=150,
                        temperature=0.7
                    )
                    reply = resp.choices[0].message.content.strip()
                except Exception as e:
                    print(f"Erro ao chamar OpenAI: {e}")
                    reply = "Cansei de responder, só falo no próximo mês seu merda!"

            await message.reply(reply, mention_author=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(ChatGPTListener(bot))