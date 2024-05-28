DROP MATERIALIZED VIEW IF EXISTS historial_paciente;

CREATE MATERIALIZED VIEW historial_paciente AS
SELECT
    c.id,
    c.ssn,
    c.nif,
    c.nome,
    c.data,
    EXTRACT(YEAR FROM c.data) AS ano,
    EXTRACT(MONTH FROM c.data) AS mes,
    EXTRACT(DAY FROM c.data) AS dia_do_mes,
    EXTRACT(DOW FROM c.data) AS dia_da_semana,
    SUBSTRING(cl.morada FROM LENGTH(cl.morada) - POSITION(' ' IN REVERSE(cl.morada)) + 2) AS localidade,
    m.especialidade,
    'observacao' AS tipo,
    o.parametro AS chave,
    o.valor
FROM
    consulta c
JOIN
    observacao o ON c.id = o.id
JOIN
    clinica cl ON c.nome = cl.nome
JOIN
    medico m ON c.nif = m.nif

UNION ALL

SELECT
    c.id,
    c.ssn,
    c.nif,
    c.nome,
    c.data,
    EXTRACT(YEAR FROM c.data) AS ano,
    EXTRACT(MONTH FROM c.data) AS mes,
    EXTRACT(DAY FROM c.data) AS dia_do_mes,
    EXTRACT(DOW FROM c.data) AS dia_da_semana,
    cl.morada AS localidade,
    m.especialidade,
    'receita' AS tipo,
    r.medicamento AS chave,
    r.quantidade AS valor
FROM
    consulta c
JOIN
    receita r ON c.codigo_sns = r.codigo_sns
JOIN
    clinica cl ON c.nome = cl.nome
JOIN
    medico m ON c.nif = m.nif;
