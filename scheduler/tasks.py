import logging
import discord
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from zoneinfo import ZoneInfo
from datetime import datetime, timedelta
from db import fetchall

TZ_BR = ZoneInfo("America/Sao_Paulo")

scheduler = AsyncIOScheduler(timezone=TZ_BR)

def setup_scheduler(bot: discord.Client):
    # Job Enquete diária às 07:00 (horário de SP)
    scheduler.add_job(
        func=lambda: bot.loop.create_task(enviar_enquete(bot)),
        trigger=CronTrigger(hour=7, minute=0, timezone=TZ_BR),
        id="daily_enquete",
        replace_existing=True,
        name="Enquete do Dia às 07:00 (SP)"
    )

    # Job Resumo diário às 23:00 (horário de SP)
    scheduler.add_job(
        func=lambda: bot.loop.create_task(enviar_resumo(bot)),
        trigger=CronTrigger(hour=23, minute=0, timezone=TZ_BR),
        id="daily_resumo",
        replace_existing=True,
        name="Resumo Diário às 23:00 (SP)"
    )

    if not scheduler.running:
        scheduler.start()
        logging.info("Scheduler iniciado com timezone America/Sao_Paulo")

async def enviar_enquete(bot: discord.Client):
    now_sp = datetime.now(TZ_BR)
    for guild in bot.guilds:
        conf = fetchall(
            "SELECT canal_configurado FROM configuracoes WHERE guild_id = %s",
            (guild.id,)
        )
        if not conf:
            continue
        canal = bot.get_channel(conf[0][0])
        if canal:
            embed = discord.Embed(
                title="☀️ Enquete do Dia",
                description=(
                    "Qual sua vibe hoje?\n\n"
                    "🟨 EITCHAAAAAA\n"
                    "🔵 OPA...\n"
                    "🟢 TCHUDU BEM\n"
                    "🔴 FUI BUSCAR O CRACHÁ"
                ),
                color=discord.Color.yellow(),
                timestamp=now_sp
            )
            embed.set_footer(text="Vote antes da meia-noite!")
            await canal.send(embed=embed)

async def enviar_resumo(bot: discord.Client):
    now_sp = datetime.now(TZ_BR)
    today = now_sp.date()
    for guild in bot.guilds:
        conf = fetchall(
            "SELECT canal_configurado FROM configuracoes WHERE guild_id = %s",
            (guild.id,)
        )
        if not conf:
            continue
        canal = bot.get_channel(conf[0][0])
        if not canal:
            continue

        resumo = fetchall("""
            SELECT usuario_nome, SUM(EXTRACT(EPOCH FROM (saida - entrada))) AS total_segundos
            FROM sessoes_voz
            WHERE guild_id = %s AND entrada::date = %s
            GROUP BY usuario_nome
            ORDER BY total_segundos DESC
        """, (guild.id, today))
        if not resumo:
            continue

        mais_ativo = resumo[0][0]
        longas = [r for r in resumo if r[1] > 3600]
        media_segundos = sum(r[1] for r in resumo) / len(resumo)
        media_formatada = str(timedelta(seconds=int(media_segundos)))

        embed = discord.Embed(
            title="📊 Resumo Diário",
            color=discord.Color.dark_blue(),
            timestamp=now_sp
        )
        embed.add_field(name="Sessões com +1h", value=str(len(longas)), inline=True)
        embed.add_field(name="Média por sessão", value=media_formatada, inline=True)
        embed.add_field(name="Mais ativo", value=mais_ativo, inline=True)
        embed.set_footer(text="Boa noite, e continue firme amanhã!")
        await canal.send(embed=embed)
