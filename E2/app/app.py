#!/usr/bin/python3
# Copyright (c) BDist Development Team
# Distributed under the terms of the Modified BSD License.
import os
from logging.config import dictConfig

from datetime import datetime, timezone, timedelta
from flask import Flask, jsonify, request
from psycopg.rows import namedtuple_row
from psycopg_pool import ConnectionPool
import psycopg

# postgres://username:password@hostname/database_name
DATABASE_URL = os.environ.get("DATABASE_URL", "postgres://postgres:postgres@postgres/saude")

pool = ConnectionPool(
    conninfo=DATABASE_URL,
    kwargs={
        "autocommit": True,  # If True don’t start transactions automatically.
        "row_factory": namedtuple_row,
    },
    min_size=4,
    max_size=10,
    open=True,
    name="postgres_pool",
    timeout=5,
)

dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s in %(module)s:%(lineno)s - %(funcName)20s(): %(message)s",
            }
        },
        "handlers": {
            "wsgi": {
                "class": "logging.StreamHandler",
                "stream": "ext://flask.logging.wsgi_errors_stream",
                "formatter": "default",
            }
        },
        "root": {"level": "INFO", "handlers": ["wsgi"]},
    }
)

app = Flask(__name__)
app.config.from_prefixed_env()
log = app.logger

@app.route("/", methods=("GET",))
def listaClinicas():
    """Lista todas as clinicas."""

    with pool.connection() as conn:
        with conn.cursor() as cur:
            clinicas = cur.execute(
                """
                SELECT nome, morada
                FROM clinica;
                """,
                {},
            ).fetchall()

    return jsonify(clinicas), 200

@app.route("/c/<clinica>", methods=("GET",))
def listaEspecialidadesClinica(clinica):
    """Lista todas as especialidades de uma clinica."""
    if existeClinica(clinica) == False:
        return jsonify(f"A clinica {clinica} não existe."), 400
    
    with pool.connection() as conn:
        with conn.cursor() as cur:
            especialidades = cur.execute(
                """
                SELECT DISTINCT medico.especialidade
                FROM clinica JOIN trabalha USING(nome) JOIN medico USING(nif)
                WHERE clinica.nome=%(clinica)s;
                """,
                {"clinica": clinica},
            ).fetchall()

    return jsonify(especialidades), 200

def existeClinica(clinica):
    with pool.connection() as conn:
        with conn.cursor() as cur:
            clinica = cur.execute(
                """
                SELECT nome FROM clinica WHERE nome=%(clinica)s;
                """,
                {"clinica":clinica},
            ).fetchone()
        
    return clinica != None

@app.route("/c/<clinica>/<especialidade>", methods=("GET",))
def listaMedicosSlots(clinica, especialidade):
    """Lista todos os médicos da clinica e da especialidade e os 3 próximos horários disponíveis para consulta"""

    error = None
    
    if existeClinica(clinica) == False:
        error = f"A clinica {clinica} não existe."
    elif existeEspecialidade(especialidade, clinica) == False:
        error = f"A especialidade {especialidade} não existe na clinica {clinica}."

    if error is not None:
        return jsonify(error), 400
    
    dowMedicos = {}
    data_atual = datetime.now().date()
    hora_atual = datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=1))).time()
    
    """
    dicionario da forma:  
        {
            (nomeMedico, nifMedico): [0,1,2],
            (nomeMedico2, nifMedico2): [3,4,5]
        }
    """
    with pool.connection() as conn:
        with conn.cursor() as cur:
            medico = cur.execute(
                """
                SELECT medico.nome AS nome, medico.nif AS nif, trabalha.dia_da_semana AS dow
                FROM medico JOIN trabalha USING(nif)
                WHERE trabalha.nome=%(clinica)s AND medico.especialidade=%(especialidade)s;
                """,
                {"clinica":clinica,"especialidade":especialidade},
            ).fetchone()

            while medico:
                #se médico ainda nao está no dicionário
                if (medico.nome,medico.nif) not in list(dowMedicos):
                    dowMedicos[(medico.nome,medico.nif)] = [medico.dow]
                else:
                    dowMedicos[(medico.nome, medico.nif)].append(medico.dow)
                medico = cur.fetchone()
                
            consultasMedicos = []
            for dowMedico in list(dowMedicos):
                
                consultasMedico = cur.execute(
                    """
                    SELECT %(nome_medico)s, horas_disponiveis.data, horas_disponiveis.hora FROM 
                        (SELECT dia AS data, hora
                         FROM calendario
                         WHERE (dia > %(data_atual)s
                        OR (dia = %(data_atual)s AND hora > %(hora_atual)s)) AND EXTRACT(DOW FROM dia) = ANY (%(dias_da_semana)s)
                        EXCEPT
                        SELECT data, hora
                        FROM consulta
                        WHERE nome=%(clinica)s AND nif = %(nif_medico)s AND (data > %(data_atual)s
                        OR (data = %(data_atual)s AND hora > %(hora_atual)s))) AS horas_disponiveis 
                        ORDER BY horas_disponiveis.data, horas_disponiveis.hora ASC;
                    """,
                    {"clinica":clinica, "nif_medico":dowMedico[1], "data_atual":data_atual, "hora_atual":hora_atual, "nome_medico":dowMedico[0], "dias_da_semana": dowMedicos[dowMedico]},
                ).fetchmany(3)
                
                consultasMedicos.extend((dowMedico[0], row[1].isoformat(), row[2].strftime("%H:%M:%S")) for row in consultasMedico)

    return jsonify(consultasMedicos), 200

def existeEspecialidade(especialidade, clinica):
    with pool.connection() as conn:
        with conn.cursor() as cur:
            especialidade = cur.execute(
                """
                SELECT medico.especialidade
                FROM medico JOIN trabalha USING(nif)
                WHERE trabalha.nome=%(clinica)s AND medico.especialidade=%(especialidade)s;
                """,
                {"clinica":clinica,"especialidade":especialidade},
            ).fetchone()
        
    return especialidade != None

@app.route("/a/<clinica>/marcar", methods=("POST",))
def marcaConsulta(clinica):
    paciente=request.args.get("paciente")
    medico=request.args.get("medico")
    data=request.args.get("data")
    hora=request.args.get("hora")

    error = None

    if existeClinica(clinica) == False:
        error = f"A clinica {clinica} não existe."
    elif existeMedico(medico) == False:
        error = f'O médico {medico} não existe'  
    elif existePaciente(paciente) == False:
        error = f'O paciente {paciente} não existe'
    elif horaFutura(data,hora) == False:
        error = f'Data de marcação inválida.'
    elif verificaSlotMedico(medico, data, hora) == False:
        error = f'O médico {medico} já tem uma consulta marcada para a data {data} e hora {hora}.'
    elif verificaSlotPaciente(paciente, data, hora) == False:
        error = f'O paciente{paciente} já tem uma consulta marcada para a data {data} e hora {hora}.'

    if error is not None:
        return jsonify(error), 400

    try:
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO consulta (ssn, nif, nome, data, hora) VALUES(%(ssn)s, %(nif)s, %(clinica)s, %(data)s, %(hora)s)
                    """,
                    {"clinica": clinica, "nif": medico, "ssn": paciente, "data": data, "hora": hora},
                )
        
        msg = f'A sua marcação foi cumprida. Será no dia {data} às {hora} na clínica {clinica} com o médico {medico}. Obrigado pela confiança, boa consulta!'
        return jsonify(msg), 200
        
    except psycopg.errors.RaiseException as e:
        erro = str(e)
        if 'verifica_clinica' in str(e):
            erro = 'O médico não trabalha nessa consulta nesse dia da semana. Por favor, selecione outra clinica ou outro médico.'
        elif 'verifica_auto_consulta' in str(e):
            erro = 'Um médico não se pode consultar a si próprio. Por favor, selecione outro medico ou paciente.'
        msg_error = f'Não foi possível marcar a sua consulta devido ao seguinte erro: {erro}'
        return jsonify(msg_error), 400
    except psycopg.IntegrityError as e:
        erro = str(e)
        if 'restricaotempo' in str(e):
            erro = 'As consultas têm de ser à hora exata ou a uma meia hora e a hora do incio da consulta tem de ser entre as 8 e o 12:30 ou as 14 e as 18:30. Por favor, mude a hora para marcar a sua consulta.'
        msg_error = f'Não foi possível marcar a sua consulta devido ao seguinte erro: {erro}'
        return jsonify(msg_error), 400

def existeMedico(medico):
    with pool.connection() as conn:
        with conn.cursor() as cur:
            medico = cur.execute(
                """
                SELECT nif FROM medico WHERE nif=%(medico)s;
                """,
                {"medico":medico},
            ).fetchone()
        
    return medico != None

def existePaciente(paciente):
    with pool.connection() as conn:
        with conn.cursor() as cur:
            paciente = cur.execute(
                """
                SELECT ssn FROM paciente WHERE ssn=%(paciente)s;
                """,
                {"paciente":paciente},
            ).fetchone()
        
    return paciente != None

def horaFutura(data_str, hora_str):
    agora = datetime.now()

    data_atual = agora.date()
    hora_atual = agora.time()

    data = datetime.strptime(data_str, "%Y-%m-%d").date()
    hora = datetime.strptime(hora_str, "%H:%M:%S").time()

    if data < data_atual:
        return False
    else:
        if data_atual == data and hora <= hora_atual:
            return False
        return True

def verificaSlotMedico(medico, data, hora):
    with pool.connection() as conn:
        with conn.cursor() as cur:
            consulta = cur.execute(
                """
                SELECT nif FROM consulta WHERE nif=%(medico)s AND data=%(data)s AND hora=%(hora)s;
                """,
                {"medico":medico,"data":data,"hora":hora},
            ).fetchone()
        
    return consulta == None

def verificaSlotPaciente(paciente, data, hora):
    with pool.connection() as conn:
        with conn.cursor() as cur:
            consulta = cur.execute(
                """
                SELECT ssn FROM consulta WHERE ssn=%(paciente)s AND data=%(data)s AND hora=%(hora)s;
                """,
                {"paciente":paciente,"data":data,"hora":hora},
            ).fetchone()
        
    return consulta == None


@app.route("/a/<clinica>/cancelar", methods=("POST",))
def cancelarConsulta(clinica):
    paciente=request.args.get("paciente")
    medico=request.args.get("medico")
    data=request.args.get("data")
    hora=request.args.get("hora")

    error = None

    if existeClinica(clinica) == False:
        error = f"A clinica {clinica} não existe."
    elif existeMedico(medico) == False:
        error = f'O médico {medico} não existe'  
    elif existePaciente(paciente) == False:
        error = f'O paciente {paciente} não existe'
    elif horaFutura(data,hora) == False:
        error = f'Data de desmarcação inválida.'
    elif verificaExisteConsulta(medico, paciente, data, hora, clinica) == False:
        error = f'Não há consultas marcadas para a data {data}, hora {hora} com o paciente {paciente}, o médico {medico} e na clinica {clinica}.'

    if error is not None:
        return jsonify(error), 400

    with pool.connection() as conn:
        with conn.cursor() as cur:
            with conn.transaction():
                consulta=cur.execute(
                    """
                    SELECT id, codigo_sns FROM consulta WHERE ssn=%(paciente)s and nif=%(medico)s and data=%(data)s and hora=%(hora)s
                    """,
                    {"paciente":paciente, "medico":medico, "data":data, "hora":hora}
                ).fetchone()

                cur.execute(
                    """
                    DELETE FROM observacao
                    WHERE id = %(id)s
                    """,
                    {"id": consulta.id},
                )
                if consulta.codigo_sns != None:
                    cur.execute(
                        """
                        DELETE FROM receita
                        WHERE codigo_sns = %(codigo_sns)s 
    
                        """,
                        {"codigo_sns": consulta.codigo_sns},
                    )
                cur.execute(
                    """
                    DELETE FROM consulta
                    WHERE id = %(id)s 
                    """,
                    {"id": consulta.id},
                )
                
    return jsonify(f'A sua consulta foi desmarcada com sucesso. Obrigado, volte sempre!'), 200


def verificaExisteConsulta(medico, paciente, data, hora, clinica):
    with pool.connection() as conn:
        with conn.cursor() as cur:
            consulta = cur.execute(
                """
                SELECT ssn FROM consulta WHERE ssn=%(paciente)s AND nif=%(medico)s AND data=%(data)s AND hora=%(hora)s AND nome=%(clinica)s;
                """,
                {"medico":medico,"paciente":paciente,"data":data,"hora":hora, "clinica": clinica},
            ).fetchone()
        
    return consulta != None


if __name__ == "__main__":
    app.run()
