from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
from db import fetchall
import discord

scheduler = AsyncIOScheduler()

def setup_scheduler(bot):
    @scheduler.scheduled_job("cron", hour=7, minute=0)
    async def enviar_enquete():
        for guild in bot.guilds:
            conf = fetchall("SELECT canal_configurado FROM configuracoes WHERE guild_id = %s", (guild.id,))
            if conf:
                canal = bot.get_channel(conf[0][0])
                if canal:
                    embed = discord.Embed(
                        title="☀️ Enquete do Dia",
                        description="Qual sua vibe hoje?\n\n🟨 EITCHAAAAAA\n🔵 OPA...\n🟢 TCHUDU BEM\n🔴 FUI BUSCAR O CRACHÁ",
                        color=discord.Color.yellow()
                    )
                    embed.set_footer(text="Vote antes da meia-noite!")
                    await canal.send(embed=embed)

    @scheduler.scheduled_job("cron", hour=23, minute=0)
    async def enviar_resumo():
        now = datetime.utcnow()
        for guild in bot.guilds:
            canal_id = fetchall("SELECT canal_configurado FROM configuracoes WHERE guild_id = %s", (guild.id,))
            if not canal_id:
                continue

            resumo = fetchall("""
                SELECT usuario_nome, SUM(tempo_sessao) as total
                FROM sessoes_voz
                WHERE guild_id = %s AND entrada::date = %s
                GROUP BY usuario_nome ORDER BY total DESC
            """, (guild.id, now.date()))

            if not resumo:
                continue

            mais_ativo = resumo[0][0]
            longas = [r for r in resumo if r[1] and r[1].total_seconds() > 3600]
            medias = sum(r[1].total_seconds() for r in resumo) / len(resumo)
            medias = str(timedelta(seconds=int(medias)))

            embed = discord.Embed(
                title="📊 Resumo Diário",
                color=discord.Color.dark_blue()
            )
            embed.add_field(name="Sessões com +1h", value=str(len(longas)), inline=True)
            embed.add_field(name="Média por sessão", value=medias, inline=True)
            embed.add_field(name="Mais ativo", value=mais_ativo, inline=True)
            embed.set_footer(text="Boa noite, e continue firme amanhã!")
            embed.timestamp = now

            canal = bot.get_channel(canal_id[0][0])
            if canal:
                await canal.send(embed=embed)

    scheduler.start()