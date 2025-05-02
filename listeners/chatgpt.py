import os
import discord
from discord.ext import commands
from openai import OpenAI, OpenAIError
from huggingface_hub import InferenceApi
from dotenv import load_dotenv

# carrega .env
load_dotenv()

# instância OpenAI
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
)

# instância HuggingFace Inference (usa anon se HF_API_TOKEN não estiver setado)
hf_client = InferenceApi(
    repo_id=os.getenv("HF_MODEL", "tiiuae/falcon-7b-instruct"),
    token=os.getenv("HF_API_TOKEN", "")
)

# modelo OpenAI via .env
MODEL = os.getenv("MODEL", "gpt-3.5-turbo")

# persona do Araujo
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
        # ignora bots e comandos slash
        if message.author.bot or message.content.startswith(self.bot.command_prefix):
            return

        # só responde a menções
        if self.bot.user in message.mentions:
            prompt = message.content.replace(f"<@!{self.bot.user.id}>", "").strip()
            async with message.channel.typing():
                # 1) tenta OpenAI
                try:
                    resp = client.chat.completions.create(
                        model=MODEL,
                        messages=[
                            {"role": "system", "content": SYSTEM_PERSONA},
                            {"role": "user",   "content": prompt}
                        ],
                        max_tokens=150,
                        temperature=0.7
                    )
                    reply = resp.choices[0].message.content.strip()

                # 2) em caso de cota estourada ou qualquer erro, usa HF
                except OpenAIError as oe:
                    code = getattr(oe, "code", "")
                    if code == "insufficient_quota":
                        # fallback gratuito
                        payload = {
                            "inputs": SYSTEM_PERSONA + "\n\nUsuário: " + prompt,
                            "parameters": {"max_new_tokens": 150, "temperature": 0.7}
                        }
                        hf_resp = hf_client(payload)
                        reply = hf_resp.get("generated_text", "Não consegui gerar nada.")
                    else:
                        # outros erros do OpenAI, também pode fallback
                        try:
                            payload = {
                                "inputs": SYSTEM_PERSONA + "\n\nUsuário: " + prompt,
                                "parameters": {"max_new_tokens": 150, "temperature": 0.7}
                            }
                            hf_resp = hf_client(payload)
                            reply = hf_resp.get("generated_text", "Erro geral, não rolou aqui.")
                        except Exception:
                            reply = "Cansei de responder, só falo no próximo mês seu merda!"

                except Exception:
                    # fallback genérico
                    try:
                        payload = {
                            "inputs": SYSTEM_PERSONA + "\n\nUsuário: " + prompt,
                            "parameters": {"max_new_tokens": 150, "temperature": 0.7}
                        }
                        hf_resp = hf_client(payload)
                        reply = hf_resp.get("generated_text", "Erro geral, não rolou aqui.")
                    except Exception:
                        reply = "Cansei de responder, só falo no próximo mês seu merda!"

            await message.reply(reply, mention_author=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(ChatGPTListener(bot))