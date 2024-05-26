INSERT INTO consulta (ssn, nif, nome, data, hora, codigo_sns) VALUES('30591746307','396939652','Gonzaga','2023-01-01','13:30:00','337874010196');
INSERT INTO consulta (ssn, nif, nome, data, hora, codigo_sns) VALUES('30591746307','396939652','Gonzaga','2023-01-01','15:53:00','337874010196');
SELECT * FROM consulta WHERE hora = '13:30:00' OR hora = '15:53:00';
INSERT INTO paciente VALUES('11111111111','396939652','Rita Monteiro','925641554','Largo da Praia da Galé 94 5047-002 Barreiro','1977-10-28');
INSERT INTO consulta (ssn, nif, nome, data, hora, codigo_sns) VALUES('11111111111','396939652','Gonzaga','2023-01-01','15:00:00','111111111111');
SELECT * FROM consulta WHERE ssn = '11111111111' AND nif = '396939652';
DELETE FROM paciente WHERE ssn = '11111111111';
INSERT INTO consulta (ssn, nif, nome, data, hora, codigo_sns) VALUES('15693765779','396939652','Cuf','2023-01-01','11:00:00','121212121212');
SELECT * FROM consulta WHERE nif = '396939652' AND nome = 'Cuf' AND data = '2023-01-01';