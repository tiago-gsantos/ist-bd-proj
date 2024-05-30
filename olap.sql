--OLAP:1

WITH consulta_ortopedia AS
    (SELECT ssn, data, chave AS parametro
    FROM
        historial_paciente
    WHERE
        especialidade = 'ortopedia' AND 
        valor IS NULL AND
        tipo = 'observacao'),
pares_consultas_mesmo_sintoma AS
    (SELECT c1.ssn, c2.data-c1.data AS intervalo
    FROM 
        consulta_ortopedia c1, consulta_ortopedia c2
    WHERE
        c1.parametro = c2.parametro AND
        c1.data < c2.data AND
        c1.ssn = c2.ssn)
SELECT ssn, MAX(intervalo) AS indicador_progresso
FROM
    pares_consultas_mesmo_sintoma
GROUP BY ssn
ORDER BY indicador_progresso DESC;

--OLAP:2

SELECT DISTINCT chave
FROM 
   historial_paciente h1
WHERE
    tipo = 'receita' AND
    especialidade='cardiologia' AND
    EXISTS (SELECT 1 FROM historial_paciente h2
    WHERE h2.tipo = 'receita' AND
    h2.especialidade='cardiologia' AND h2.chave=h1.chave AND h2.ssn=h1.ssn 
    AND h2.data >= (h1.date - INTERVAL '1 year')
    AND h2.data <= h1.date
    HAVING COUNT(DISTINCT month) = 12
    );


--OLAP:3
WITH historial_paciente_com_nome_medico AS (
    SELECT id, chave AS medicamento, localidade, hp.nome AS clinica, mes, dia_do_mes, hp.especialidade, medico.nome AS nome_medico, valor FROM
    historial_paciente hp JOIN medico USING(nif)
    WHERE tipo='receita'
)

SELECT medicamento, mes, dia_do_mes, localidade, clinica, especialidade, nome_medico,
SUM(valor) AS qtd_total_receitadas
FROM
    historial_paciente_com_nome_medico
GROUP BY GROUPING SETS((medicamento), (medicamento, localidade), (medicamento, localidade, clinica),
(medicamento, mes), (medicamento, mes, dia_do_mes), (medicamento, especialidade),
(medicamento, especialidade, nome_medico)) 
ORDER BY medicamento, mes, dia_do_mes, localidade, clinica, especialidade, nome_medico;

--OLAP:4


WITH historial_paciente_com_nome_medico_2 AS (
    SELECT id, hp.nome AS clinica, hp.especialidade, medico.nome AS nome_medico, valor FROM
    historial_paciente hp JOIN medico USING(nif) 
    WHERE valor IS NOT NULL
)

SELECT especialidade, nome_medico, clinica, AVG(valor) AS qtd_media,
STDDEV_POP(valor) AS desvio_padrao_qtd
FROM
    historial_paciente_com_nome_medico_2
GROUP BY GROUPING SETS((), (especialidade), (especialidade, nome_medico), (clinica),
(especialidade, clinica), (especialidade, nome_medico, clinica)) 
ORDER BY medicamento, mes, dia_do_mes, localidade, clinica, especialidade, nome_medico;
