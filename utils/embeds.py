import discord
from datetime import datetime

def embed_sucesso(mensagem):
    embed = discord.Embed(
        title="✅ Ação concluída",
        description=mensagem,
        color=discord.Color.green()
    )
    embed.set_footer(text="Você pode usar /ajuda para mais comandos.")
    embed.timestamp = datetime.utcnow()
    return embed

def embed_erro(erro, sugestao):
    embed = discord.Embed(
        title="❌ Algo deu errado",
        color=discord.Color.red()
    )
    embed.add_field(name="Erro", value=erro, inline=False)
    embed.add_field(name="Solução sugerida", value=sugestao, inline=False)
    embed.set_footer(text="Se o problema persistir, contate um administrador.")
    embed.timestamp = datetime.utcnow()
    return embed

def embed_alerta(tipo, descricao, funcao):
    embed = discord.Embed(
        title="🚨 Alerta do Sistema",
        color=discord.Color.orange()
    )
    embed.add_field(name="Tipo", value=tipo)
    embed.add_field(name="Descrição", value=descricao)
    embed.add_field(name="Função afetada", value=funcao)
    embed.set_footer(text="Alerta automático de integridade do bot")
    embed.timestamp = datetime.utcnow()
    return embed