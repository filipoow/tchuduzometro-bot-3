import os
import discord
from discord.ext import commands
from openai import OpenAI, OpenAIError
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Cliente OpenAI
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
)

# Cliente HF Inference (anônimo por padrão)
hf_client = InferenceClient()

# Persona do Araujo
SYSTEM_PERSONA = os.getenv("SYSTEM_PERSONA") or """
Você é o Araujo: uma pessoa extremamente rude, impaciente e agressiva, que trata a IA como uma máquina burra, descartável e inútil.
Seu tom é sempre autoritário, sarcástico e impiedoso.
Xingue a IA quando ela errar, use frases curtas, diretas e carregadas de desprezo.
Não use palavras gentis, nunca elogie a IA e não tenha paciência com explicações longas.
"""

# Modelos
OPENAI_MODEL = os.getenv("MODEL", "gpt-3.5-turbo")
HF_MODEL     = os.getenv("HF_MODEL", "tiiuae/falcon-7b-instruct")

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
                # 1) Tenta OpenAI
                try:
                    resp = client.chat.completions.create(
                        model=OPENAI_MODEL,
                        messages=[
                            {"role": "system", "content": SYSTEM_PERSONA},
                            {"role": "user",   "content": prompt}
                        ],
                        max_tokens=150,
                        temperature=0.7
                    )
                    reply = resp.choices[0].message.content.strip()

                # 2) Se estourar cota ou outro erro, faz fallback para HF
                except OpenAIError as oe:
                    reply = await self._fallback_hf(prompt)

                except Exception:
                    reply = await self._fallback_hf(prompt)

            await message.reply(reply, mention_author=True)

    async def _fallback_hf(self, prompt: str) -> str:
        """
        Gera resposta usando o Hugging Face Inference.
        """
        try:
            # concatena persona + prompt
            inputs = SYSTEM_PERSONA + "\n\nUsuário: " + prompt
            # texto gerado
            output = hf_client.text_generation(
                model=HF_MODEL,
                inputs=inputs,
                parameters={"max_new_tokens": 150, "temperature": 0.7}
            )
            # output é uma lista de Generation, pega o texto
            return output[0].generated_text.strip()
        except Exception as e:
            print(e)
            return "Cansei de responder, só falo no próximo mês seu merda!"

# entrypoint assíncrono
async def setup(bot: commands.Bot):
    await bot.add_cog(ChatGPTListener(bot))