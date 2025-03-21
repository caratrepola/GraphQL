from flask import Flask, request, jsonify, send_file
from ariadne import gql, make_executable_schema, ObjectType, graphql_sync
from database import create_app, db
from models import User, Event, Registrazione
import os
from flask_cors import CORS
from datetime import datetime


app = create_app()

CORS(app)

# Definizione dello schema GraphQL con Query
type_defs = gql("""
type User {
    id: ID!
    name: String!
    email: String!
}

type Event {
    id: ID!
    titolo: String!
    descrizione: String!
    data: String!
    luogo: String!
}

type Registration {
    id: ID!
    user_id: ID!
    event_id: ID!
    data_registrazione: String!
}

type Query {
    _empty: String
}

type Mutation {
    createUser(name: String!, email: String!): User
    createEvent(titolo: String!, descrizione: String!, data: String!, luogo: String!): Event
    updateUser(id: ID!, name: String, email: String): User
    registerUserToEvent(userId: ID!, eventId: ID!): Registration
    cancelRegistration(registrationId: ID!): Boolean
}
""")

query = ObjectType("Query")  # Tipo Query vuoto per evitare errori
mutation = ObjectType("Mutation")


# Mutazione per creare un nuovo utente
@mutation.field("createUser")
def resolve_create_user(_, info, name, email):
    new_user = User(name=name, email=email)
    db.session.add(new_user)
    db.session.commit()
    return new_user.to_dict()


# Mutazione per creare un nuovo evento
@mutation.field("createEvent")
def resolve_create_event(_, info, titolo, descrizione, data, luogo):
    data_obj = datetime.fromisoformat(data.replace("Z", "+00:00"))
    new_event = Event(titolo=titolo, descrizione=descrizione, data=data_obj, luogo=luogo)
    db.session.add(new_event)
    db.session.commit()
    return new_event.to_dict()


# Mutazione per aggiornare le informazioni di un utente esistente
@mutation.field("updateUser")
def resolve_update_user(_, info, id, name=None, email=None):
    user = User.query.get(id)
    if not user:
        return {"error": "Utente non trovato"}
    if name:
        user.name = name
    if email:
        user.email = email
    db.session.commit()
    return user.to_dict()


# Mutazione per registrare un utente a un evento
@mutation.field("registerUserToEvent")
def resolve_register_user_to_event(_, info, userId, eventId):
    user = User.query.get(userId)
    event = Event.query.get(eventId)
    if not user or not event:
        return {"error": "Utente o evento non trovato"}

    registration = Registrazione(user_id=userId, event_id=eventId)
    db.session.add(registration)
    db.session.commit()
    return registration.to_dict()


# Mutazione per annullare la registrazione a un evento
@mutation.field("cancelRegistration")
def resolve_cancel_registration(_, info, registrationId):
    registration = Registrazione.query.get(registrationId)
    if not registration:
        return False

    db.session.delete(registration)
    db.session.commit()
    return True


# Creazione dello schema GraphQL con Query e Mutation
schema = make_executable_schema(type_defs, query, mutation)

@app.route("/graphql/2", methods=["POST", "GET"])
def graphql_server():
    # Gestisci sia POST che GET
    if request.method == "GET":
        file_path = os.path.join(os.getcwd(), "graphql-client_punto2.html")
        return send_file(file_path)

    data = request.get_json()
    success, result = graphql_sync(schema, data, context_value=request, debug=True)
    status_code = 200 if success else 400
    return jsonify(result), status_code

if __name__ == "__main__":
    app.run(debug=True)
