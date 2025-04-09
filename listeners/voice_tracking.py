import discord
from discord.ext import commands
from datetime import datetime
from db import execute, fetchall

entrada_usuarios = {}

class VoiceTracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if not member.guild or member.bot:
            return

        now = datetime.utcnow()

        if after.channel and not before.channel:
            entrada_usuarios[member.id] = now

        elif before.channel and not after.channel:
            entrada = entrada_usuarios.pop(member.id, None)
            if not entrada:
                return

            tempo_sessao = now - entrada
            conf = fetchall("SELECT tempo_para_xp, xp_por_intervalo, coeficiente_progresso FROM configuracoes WHERE guild_id = %s", (member.guild.id,))
            if not conf:
                return

            tempo_para_xp, xp_por_intervalo, coef = conf[0]
            segundos = tempo_sessao.total_seconds()
            xp_ganho = int((segundos // (tempo_para_xp * 60)) * xp_por_intervalo)

            total_xp = fetchall("SELECT COALESCE(MAX(xp_total), 0) FROM sessoes_voz WHERE usuario_id = %s AND guild_id = %s", (member.id, member.guild.id))[0][0]
            xp_total = total_xp + xp_ganho
            nivel = 1
            while xp_total >= xp_por_intervalo * (coef ** nivel):
                nivel += 1

            execute("""
                INSERT INTO sessoes_voz (guild_id, canal_id, usuario_id, usuario_nome, entrada, saida, tempo_sessao, xp_ganho, xp_total, nivel)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                member.guild.id, before.channel.id, member.id, member.display_name,
                entrada, now, tempo_sessao, xp_ganho, xp_total, nivel
            ), commit=True)

async def setup(bot):
    await bot.add_cog(VoiceTracker(bot))
