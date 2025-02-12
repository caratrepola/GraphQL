from flask import Flask, request, jsonify
from ariadne import QueryType, make_executable_schema, graphql_sync
import requests

# Endpoint dell'API esterna
API_ESTERNA = "https://external-app.com/api"


# Funzioni
def recupera_utente_per_id(id_utente):
    response = requests.get(f"{API_ESTERNA}/users/{id_utente}")
    if response.status_code == 200 and isinstance(response.json(), dict):
        return response.json()
    return None


def recupera_evento_per_id(id_evento):
    response = requests.get(f"{API_ESTERNA}/events/{id_evento}")
    if response.status_code == 200 and isinstance(response.json(), dict):
        return response.json()
    return None


def recupera_tutti_eventi():
    response = requests.get(f"{API_ESTERNA}/events")
    if response.status_code == 200 and isinstance(response.json(), list):
        return response.json()
    return []


def recupera_tutte_registrazioni():
    response = requests.get(f"{API_ESTERNA}/registrations")
    if response.status_code == 200 and isinstance(response.json(), list):
        return response.json()
    return []

# Ariadne: Schema e Resolver
type_defs = """
    type Utente {
        id: Int
        nome: String
        email: String
    }

    type Evento {
        id: Int
        titolo: String
        data: String
        posizione: String
        partecipanti: [Utente]
    }

    type Registrazione {
        id: Int
        utente: Utente
        evento: Evento
    }

    type Query {
        utente(id: Int!): Utente
        eventi: [Evento]
        evento(id: Int!): Evento
        registrazioni: [Registrazione]
    }
"""

query = QueryType()


# Resolver per la query `utente`
@query.field("utente")
def resolver_utente(_, info, id):
    dati_utente = recupera_utente_per_id(id)
    if dati_utente:
        return dati_utente
    return None


# Resolver per la query `eventi`
@query.field("eventi")
def resolver_eventi(_, info):
    dati_eventi = recupera_tutti_eventi()
    return dati_eventi


# Resolver per la query `evento`
@query.field("evento")
def resolver_evento(_, info, id):
    dati_evento = recupera_evento_per_id(id)
    if dati_evento:
        if "partecipanti" in dati_evento:
            dati_evento["partecipanti"] = [
                recupera_utente_per_id(id_utente) for id_utente in dati_evento["partecipanti"]
            ]
        return dati_evento
    return None


# Resolver per la query `registrazioni`
@query.field("registrazioni")
def resolver_registrazioni(_, info):
    dati_registrazioni = recupera_tutte_registrazioni()
    #il cliclo serve per avere i dati piu completi altrimenti avrei solo tutti gli id
    for registrazione in dati_registrazioni:
        registrazione["utente"] = recupera_utente_per_id(registrazione["utente"])
        registrazione["evento"] = recupera_evento_per_id(registrazione["evento"])
    return dati_registrazioni


# Creazione dello schema eseguibile
schema = make_executable_schema(type_defs, query)

# Flask
app = Flask(__name__)


@app.route("/graphql_punto_1", methods=["POST"])
def graphql_server():
    data = request.get_json()
    success, result = graphql_sync(schema, data, context_value=request, debug=app.debug)
    status_code = 200 if success else 400
    return jsonify(result), status_code


if __name__ == "__main__":
    app.run(debug=True)
