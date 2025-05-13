from flask import Flask, request, jsonify, send_file
from ariadne import QueryType, make_executable_schema, graphql_sync, ObjectType
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

# Inizializzazione dell'oggetto che contiene i resolver delle query
query = QueryType()


# Resolver per ottenere un singolo utente tramite ID
@query.field("user")
def resolver_utente(_, info, id):
   # return db.session.get(User, id)
   user = db.session.get(User, id)
   if not user:
       return {
           "id": id,
           "name": "Utente non trovato",
           "email": ""
       }
   return user

# Resolver per ottenere tutti gli eventi
@query.field("eventi")
def resolver_eventi(_, info):
    eventi = db.session.query(Event).all()
    if not eventi:
        return [{
            "id": 0,
            "titolo": "Nessun evento disponibile",
            "descrizione": "",
            "data": "",
            "luogo": "",
            "partecipanti": []
        }]
    return eventi


# Resolver per ottenere un evento specifico con partecipanti
@query.field("evento")
def resolver_evento(_, info, id):
    evento = db.session.get(Event, id)
    if evento:
        return evento

    return{
        "id": id,
        "titolo": "Evento non trovato",
        "descrizione": "",
        "data": "",
        "luogo": "",
        "partecipanti": []
    }



# Resolver per ottenere tutte le registrazioni
@query.field("registrazioni")
def resolver_registrazioni(_, info):
   # return db.session.query(Registrazione).all()
   registrazioni = db.session.query(Registrazione).all()
   if not registrazioni:
       # Oggetto fittizio per comunicare che non ci sono registrazioni
       return [{
           "id": 0,
           "utente": {
               "id": 0,
               "name": "Nessuna registrazione trovata",
               "email": ""
           },
           "evento": {
               "id": 0,
               "titolo": "",
               "descrizione": "",
               "data": "",
               "luogo": "",
               "partecipanti": []
           }
       }]
   return registrazioni

# Creazione di un ObjectType per gestire i campi personalizzati del tipo Registrazione
registrazione_type = ObjectType("Registrazione")

event_type = ObjectType("Event")

# Resolver per il campo "utente" di una registrazione
@registrazione_type.field("utente")
def resolve_registrazione_utente(obj, *_):
    return db.session.get(User, obj.user_id)

# Resolver per il campo "evento" di una registrazione
@registrazione_type.field("evento")
def resolve_registrazione_evento(obj, *_):
    return db.session.get(Event, obj.event_id)

@event_type.field("partecipanti")
def resolve_event_partecipanti(obj, *_):
    return [reg.user for reg in obj.registrazioni]

# Costruzione dello schema GraphQL
schema = make_executable_schema(type_defs, query, registrazione_type, event_type)

# Definizione della rotta
@app.route("/graphqlQuery", methods=["POST", "GET"])
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
