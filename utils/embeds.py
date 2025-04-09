import discord
from datetime import datetime

def embed_sucesso(mensagem):
    return discord.Embed(
        title="✅ Ação concluída",
        description=mensagem,
        color=discord.Color.green()
    ).set_footer(text="Você pode usar /ajuda para mais comandos.").set_timestamp(datetime.utcnow())

def embed_erro(erro, sugestao):
    return discord.Embed(
        title="❌ Algo deu errado",
        color=discord.Color.red()
    ).add_field(name="Erro", value=erro, inline=False)\
     .add_field(name="Solução sugerida", value=sugestao, inline=False)\
     .set_footer(text="Se o problema persistir, contate um administrador.")\
     .set_timestamp(datetime.utcnow())

def embed_alerta(tipo, descricao, funcao):
    return discord.Embed(
        title="🚨 Alerta do Sistema",
        color=discord.Color.orange()
    ).add_field(name="Tipo", value=tipo)\
     .add_field(name="Descrição", value=descricao)\
     .add_field(name="Função afetada", value=funcao)\
     .set_footer(text="Alerta automático de integridade do bot")\
     .set_timestamp(datetime.utcnow())
