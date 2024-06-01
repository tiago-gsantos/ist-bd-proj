\copy clinica (nome, telefone, morada) FROM '~/data/clinica.csv' WITH (FORMAT csv);
\copy enfermeiro (nif, nome, telefone, morada, nome_clinica) FROM '~/data/enfermeiro.csv' WITH (FORMAT csv);
\copy medico (nif, nome, telefone, morada, especialidade) FROM '~/data/medico.csv' WITH (FORMAT csv);
\copy trabalha (nif, nome, dia_da_semana) FROM '~/data/trabalha.csv' WITH (FORMAT csv);
\copy paciente (ssn, nif, nome, telefone, morada, data_nasc) FROM '~/data/paciente.csv' WITH (FORMAT csv);
\copy consulta (ssn, nif, nome, data, hora, codigo_sns) FROM '~/data/consulta.csv' WITH (FORMAT csv);
\copy receita (codigo_sns, medicamento, quantidade) FROM '~/data/receita.csv' WITH (FORMAT csv);
\copy observacao (id, parametro, valor) FROM '~/data/observacao.csv' WITH (FORMAT csv);

    

