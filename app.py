import os
from flask import Flask, jsonify, request
import psycopg
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
    with psycopg.connect(conninfo=DATABASE_URL) as conn:
        with conn.cursor(row_factory=namedtuple_row) as cur:
            especialidades = cur.execute(
                """
                SELECT DISTINCT medico.especialidade
                FROM medico JOIN trabalha USING(nif) JOIN clinica USING(nome)
                WHERE clinica.nome=%(clinica)s;
                """,
                {"clinica":clinica,"especialidade":especialidade},
            ).fetchall()

    return jsonify(especialidades), 204



if __name__ == "__main__":
  app.run()