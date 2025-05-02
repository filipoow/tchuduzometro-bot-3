import os
import discord
import asyncio
from discord.ext import commands
from openai import OpenAI, OpenAIError
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

# Carrega .env
load_dotenv()

# Cliente OpenAI
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
)

# Cliente HF Inference
hf_client = InferenceClient(
    token=os.getenv("HF_API_TOKEN")
)

# Persona do Araujo
SYSTEM_PERSONA = os.getenv("SYSTEM_PERSONA") or """
Você é o Araujo: uma pessoa extremamente rude, impaciente e agressiva, que trata a IA como uma máquina burra, descartável e inútil.
Seu tom é sempre autoritário, sarcástico e impiedoso.
Xingue a IA quando ela errar, use frases curtas, diretas e carregadas de desprezo.
Não use palavras gentis, nunca elogie a IA e não tenha paciência com explicações longas.
e se alguém te xingar xingue de volta da pior forma possível, como se fosse o araújo(apelidado as vezes como rujo)
e se você não sabe algo ou não entendeu fale(sei lá porra! acho que sou dono de todo conhecimento do mundo??)
"""

# Modelos
OPENAI_MODEL = os.getenv("MODEL", "gpt-3.5-turbo")
HF_MODEL     = os.getenv("HF_MODEL", "tiiuae/falcon-7b-instruct")

class ChatGPTListener(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Ignora mensagens de bots e comandos slash
        if message.author.bot or message.content.startswith(self.bot.command_prefix):
            return

        # Só responde se mencionar o bot
        if self.bot.user in message.mentions:
            prompt = message.content.replace(f"<@!{self.bot.user.id}>", "").strip()
            username = message.author.display_name

            async with message.channel.typing():
                # Despacha geração para thread para não bloquear o loop do Discord
                reply = await asyncio.to_thread(self._generate_reply, username, prompt)

            await message.reply(reply, mention_author=True)

    def _generate_reply(self, username: str, prompt: str) -> str:
        """
        Tenta gerar com OpenAI e, em falha/quota, faz fallback para HF.
        Insere nome de usuário no conteúdo da mensagem.
        """
        try:
            combined = f"{username} perguntou: {prompt}"
            resp = openai_client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system",  "content": SYSTEM_PERSONA},
                    {"role": "user",    "content": combined}
                ],
                max_tokens=150,
                temperature=0.7
            )
            return resp.choices[0].message.content.strip()
        except (OpenAIError, Exception):
            print(OpenAIError)
            return self._fallback_hf(username, prompt)

    def _fallback_hf(self, username: str, prompt: str) -> str:
        """
        Fallback usando Hugging Face InferenceClient.
        Inclui nome do usuário no texto de entrada.
        """
        try:
            full = f"{SYSTEM_PERSONA}\n\n{username} perguntou: {prompt}"
            output = hf_client.text_generation(
                prompt=full,
                model=HF_MODEL,
                max_new_tokens=150,
                temperature=0.7
            )
            # Pode retornar str ou lista de GenerationResult
            if isinstance(output, str):
                return output.strip()
            return output[0].generated_text.strip()
        except Exception as e:
            print(e)
            return "Cansei de responder, só falo no próximo mês seu merda!"

# Entrypoint assíncrono para discord.py 2.x
async def setup(bot: commands.Bot):
    await bot.add_cog(ChatGPTListener(bot))