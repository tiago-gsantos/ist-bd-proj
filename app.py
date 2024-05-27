import os
from flask import Flask, jsonify, request
import psycopg
from datetime import datetime
from psycopg.rows import namedtuple_row

app = Flask(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL", "postgres://bank:bank@postgres/saude")
#postgres://username:password@postgres(nome do docker)/dbname

@app.route("/", methods=("GET",))
def listaClinicas():
    #Lista todas as clinicas
    with psycopg.connect(conninfo=DATABASE_URL) as conn:
        with conn.cursor(row_factory=namedtuple_row) as cur:
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
    #Lista todas as especialidades de uma clinica
    with psycopg.connect(conninfo=DATABASE_URL) as conn:
        with conn.cursor(row_factory=namedtuple_row) as cur:
            especialidades = cur.execute(
                """
                SELECT DISTINCT medico.especialidade
                FROM medico JOIN trabalha USING(nif) JOIN clinica USING(nome)
                WHERE clinica.nome=%(clinica)s;
                """,
                {"clinica":clinica},
            ).fetchall()

    return jsonify(especialidades), 204


@app.route("/c/<clinica>/<especialidade>", methods=("GET",))
def listaEspecialidadesClinica(clinica, especialidade):
    #Lista todas as especialidades de uma clinica
    dowMedicos = {}
    data_atual = datetime.now().date()
    hora_atual = datetime.now().time() 
    lista_horas_validas = ["8:00", "8:30","9:00","9:30","10:00","10:30","11:00","11:30","12:00","12:30"
        , "13:00", "14:00","14:30","15:00","15:30","16:00","16:30","17:00","17:30","18:00","18:30","19:00"]
    """
    dicionario da forma:  
        {
            (nomeMedico, nifMedico): [0,1,2],
            (nomeMedico2, nifMedico2): [3,4,5]
        }
    """
    with psycopg.connect(conninfo=DATABASE_URL) as conn:
        with conn.cursor(row_factory=namedtuple_row) as cur:
            medico = cur.execute(
                """
                SELECT medico.nome AS nome, medico.nif AS nif, trabalha.dia_da_semana AS dow
                FROM medico JOIN trabalha USING(nif)
                WHERE clinica.nome=%(clinica)s AND medico.especialidade=%(especialidade)s;
                """,
                {"clinica":clinica,"especialidade":especialidade},
            ).fetchone()

            while medico:
                if (medico.nif,medico.nome) not in list(dowMedicos):
                    dowMedicos[(medico.nif,medico.nome)] = [medico.dow]
                else:
                    dowMedicos[(medico.nif, medico.nome)] = dowMedicos[(medico.nif, medico.nome)].extend([(medico.nif, medico.nome)])
                medico = cur.fetchone()


            for dowMedico in list(dowMedicos):
                consultasMedico = cur.execute(
                    """
                    SELECT data, hora
                    FROM consultas
                    WHERE clinica.nome=%(clinica)s AND medico.nome = nome AND (data > data_atual
                    OR (data = data_atual AND hora > hora_atual));
                    """,
                    {"clinica":clinica, "nif_medico":dowMedico[0], "data_atual":data_atual, "hora_atual":hora_atual},
                )
                    
                
            

    return jsonify(especialidades), 204



if __name__ == "__main__":
  app.run()