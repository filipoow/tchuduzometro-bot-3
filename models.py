SCHEMA_SETUP = """
CREATE TABLE IF NOT EXISTS configuracoes (
    guild_id BIGINT PRIMARY KEY,
    nome_servidor TEXT,
    canal_configurado BIGINT,
    cargo_designado BIGINT,
    tempo_para_xp INT,
    xp_por_intervalo INT,
    coeficiente_progresso FLOAT,
    data_configuracao TIMESTAMP
);

CREATE TABLE IF NOT EXISTS interacoes (
    interacao_id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP,
    comando TEXT,
    guild_id BIGINT,
    canal_id BIGINT,
    usuario_id BIGINT,
    nome_usuario TEXT,
    parametros TEXT,
    resultado TEXT
);

CREATE TABLE IF NOT EXISTS logs (
    log_id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP,
    tipo_evento TEXT,
    descricao TEXT,
    funcionalidade TEXT,
    usuario_id BIGINT,
    dados_contexto TEXT
);

CREATE TABLE IF NOT EXISTS uso (
    evento_id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP,
    comando TEXT,
    usuario_id BIGINT,
    parametros TEXT,
    feedback TEXT
);

CREATE TABLE IF NOT EXISTS choques (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP,
    giver_id BIGINT,
    giver_nome TEXT,
    receiver_id BIGINT,
    receiver_nome TEXT,
    choques_dados INT,
    choques_recebidos INT,
    observacoes TEXT
);

CREATE TABLE IF NOT EXISTS votacoes_passou (
    votacao_id SERIAL PRIMARY KEY,
    guild_id BIGINT,
    canal_id BIGINT,
    inicio TIMESTAMP,
    fim TIMESTAMP,
    acusador_id BIGINT,
    acusador_nome TEXT,
    acusado_id BIGINT,
    acusado_nome TEXT,
    votos_sim INT,
    votos_nao INT,
    votos_condenar INT,
    resultado_final TEXT,
    lista_votantes TEXT[],
    data_finalizacao TIMESTAMP
);

CREATE TABLE IF NOT EXISTS votos_passou (
    voto_id SERIAL PRIMARY KEY,
    votacao_id INT REFERENCES votacoes_passou(votacao_id),
    votante_id BIGINT,
    timestamp TIMESTAMP,
    opcao TEXT
);

CREATE TABLE IF NOT EXISTS sessoes_voz (
    sessao_id SERIAL PRIMARY KEY,
    guild_id BIGINT,
    canal_id BIGINT,
    usuario_id BIGINT,
    usuario_nome TEXT,
    entrada TIMESTAMP,
    saida TIMESTAMP,
    tempo_sessao INTERVAL,
    xp_ganho INT,
    xp_total INT,
    nivel INT
);
"""
