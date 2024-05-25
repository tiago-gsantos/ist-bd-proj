-- (RI-1) Os horários das consultas são à hora exata ou meia-hora no horário 8-13h e 14-19h

ALTER TABLE consulta 
ADD CONSTRAINT restricaoTempo 
CHECK ((hora BETWEEN '08:00:00' AND '13:00:00' OR hora BETWEEN '14:00:00' AND '19:00:00') 
      AND
      (EXTRACT(MINUTE FROM hora) = 0 OR EXTRACT(MINUTE FROM hora) = 30));



-- (RI-2) Um médico não se pode consultar a si próprio, embora possa ser paciente de outros médicos no sistema

CREATE OR REPLACE FUNCTION verifica_auto_consulta() RETURNS TRIGGER AS
$$
DECLARE pacient_nif CHAR(9);
BEGIN
    SELECT nif INTO pacient_nif
    FROM paciente
    WHERE
        paciente.ssn == NEW.ssn;
    
    IF paciente_nif == NEW.nif THEN
            RAISE EXCEPTION 'Médico não se pode consultar a si próprio.';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE TRIGGER verifica_auto_consulta_trigger
BEFORE INSERT OR UPDATE ON consulta
FOR EACH ROW EXECUTE FUNCTION verifica_auto_consulta();



-- (RI-3) Um médico só pode dar consultas na clínica em que trabalha no dia da semana correspondente à data da consulta

CREATE OR REPLACE FUNCTION check_correct_clinic() RETURNS TRIGGER AS
$$
DECLARE clinic_name VARCHAR(80);
BEGIN
    SELECT nome INTO clinic_name
    FROM trabalha
    WHERE
        trabalha.nif == NEW.nif
        AND
        trabalha.dia_da_semana == EXTRACT(DOW FROM NEW.data);
    
    IF clinic_name != NEW.nome THEN
            RAISE EXCEPTION 'Um médico só pode dar consultas na clínica em que trabalha no dia da semana correspondente à data da consulta.';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE TRIGGER check_clinic
BEFORE INSERT OR UPDATE ON consulta
FOR EACH ROW EXECUTE FUNCTION check_correct_clinic();
