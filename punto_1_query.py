from flask import Flask, request, jsonify, send_file
from ariadne import QueryType, make_executable_schema, graphql_sync
from models import Registrazione, User, Event
from database import create_app, db
import os
from flask_cors import CORS


app = create_app()

CORS(app)


# Definizione dello schema GraphQL
type_defs = """
    type User {
        id: Int
        name: String
        email: String
    }

    type Event {
        id: Int
        titolo: String
        descrizione: String 
        data: String
        luogo: String
        partecipanti: [User]
    }

    type Registrazione {
        id: Int
        utente: User
        evento: Event
    }

    type Query {
        user(id: Int!): User
        eventi: [Event]
        evento(id: Int!): Event
        registrazioni: [Registrazione]
    }
"""

query = QueryType()


@query.field("user")
def resolver_utente(_, info, id):
    return db.session.get(User, id)


@query.field("eventi")
def resolver_eventi(_, info):
    return db.session.query(Event).all()


@query.field("evento")
def resolver_evento(_, info, id):
    evento = db.session.get(Event, id)
    if evento:
        return {
            "id": evento.id,
            "titolo": evento.titolo,
            "descrizione": evento.descrizione,
            "data": evento.data.isoformat() if evento.data else None,
            "luogo": evento.luogo,
            "partecipanti": [reg.user for reg in evento.registrazioni]
        }
    return None


@query.field("registrazioni")
def resolver_registrazioni(_, info):
    return db.session.query(Registrazione).all()


schema = make_executable_schema(type_defs, query)




@app.route("/graphql", methods=["POST", "GET"])
def graphql_server():
    # Gestisci sia POST che GET
    if request.method == "GET":
        file_path = os.path.join(os.getcwd(), "graphql-client_punto1.html")
        return send_file(file_path)  # Restituisce la pagina HTML

    # Codice esistente per gestire POST
    data = request.get_json()
    success, result = graphql_sync(schema, data, context_value=request, debug=app.debug)
    status_code = 200 if success else 400
    return jsonify(result), status_code

if __name__ == "__main__":
    app.run(debug=True)
