COPY clinica (nome, telefone, morada) FROM './data/clinica.csv' WITH (FORMAT csv);
COPY enfermeiro (nif, nome, telefone, morada, nome_clinica) FROM './data/enfermeiro.csv' WITH (FORMAT csv);
COPY medico (nif, nome, telefone, morada, especialidade) FROM './data/medico.csv' WITH (FORMAT csv);
COPY trabalha (nif, nome, dia_da_semana) FROM './data/trabalha.csv' WITH (FORMAT csv);
COPY paciente (ssn, nif, nome, telefone, morada, data_nasc) FROM './data/paciente.csv' WITH (FORMAT csv);
COPY consulta (ssn, nif, nome, data, hora, codigo_sns) FROM './data/consulta.csv' WITH (FORMAT csv);
COPY receita (codigo_sns, medicamento, quantidade) FROM './data/receita.csv' WITH (FORMAT csv);
COPY observacao (id, parametro, valor) FROM './data/observacao.csv' WITH (FORMAT csv);