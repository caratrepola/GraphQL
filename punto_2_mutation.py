from flask import Flask, request, jsonify, send_file
from ariadne import gql, make_executable_schema, ObjectType, graphql_sync
from database import create_app, db
from models import User, Event, Registrazione
import os
from flask_cors import CORS
from datetime import datetime
from graphql import GraphQLError


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

type CancelRegistrationResponse {
    success: Boolean!
    message: String!
}

type Query {
    _empty: String
}

type Mutation {
    createUser(name: String!, email: String!): User
    createEvent(titolo: String!, descrizione: String!, data: String!, luogo: String!): Event
    updateUser(id: ID!, name: String, email: String): User
    registerUserToEvent(userId: ID!, eventId: ID!): Registration
    cancelRegistration(registrationId: ID!): CancelRegistrationResponse
}
""")

query = ObjectType("Query")  # Tipo Query vuoto per evitare errori
mutation = ObjectType("Mutation")


# Mutazione per creare un nuovo utente
@mutation.field("createUser")
def resolve_create_user(_, info, name, email):
   # Controlla se esiste già un utente con lo stesso nome o email
   existing_user = User.query.filter(
       (db.func.lower(User.email) == email.lower()) |
       (db.func.lower(User.name) == name.lower())
   ).first()

   if existing_user:
       raise GraphQLError("Utente già esistente con questo nome o email")

   # Altrimenti, crea il nuovo utente
   new_user = User(name=name, email=email)
   db.session.add(new_user)
   db.session.commit()

   return {
       "id": new_user.id,
       "name": new_user.name,
       "email": new_user.email,
       "message": "Utente creato con successo"
   }


# Mutazione per creare un nuovo evento
@mutation.field("createEvent")
def resolve_create_event(_, info, titolo, descrizione, data, luogo):
    data_obj = datetime.fromisoformat(data.replace("Z", "+00:00"))
    # Controlla se esiste già un evento con lo stesso titolo e data
    existing_event = Event.query.filter(
        (Event.titolo == titolo) &
        (Event.data == data_obj)
    ).first()

    if existing_event:
        raise GraphQLError("Esiste già un evento con questo titolo e data.")

    # Se non esiste, crea il nuovo evento
    new_event = Event(
        titolo=titolo,
        descrizione=descrizione,
        data=data_obj,
        luogo=luogo
    )
    db.session.add(new_event)
    db.session.commit()

    return new_event.to_dict()

# Mutazione per aggiornare le informazioni di un utente esistente
@mutation.field("updateUser")
def resolve_update_user(_, info, id, name=None, email=None):
    user = User.query.get(id)
    if not user:
        return {"error": "Utente non trovato"}

    # Se c è un altro utente con la stessa email restituisce errore
    if email and email != user.email:
        if User.query.filter(User.email == email, User.id != id).first():
            raise GraphQLError("Email già in uso da un altro utente")

    # Applica gli aggiornamenti
    if name is not None:
        user.name = name
    if email is not None:
        user.email = email

    db.session.commit()
    return user.to_dict()


# Mutazione per registrare un utente a un evento
@mutation.field("registerUserToEvent")
def resolve_register_user_to_event(_, info, userId, eventId):
# Verifica se utente ed evento esistono
    user = User.query.get(userId)
    event = Event.query.get(eventId)
    if not user or not event:
        raise GraphQLError("Utente o evento non trovato")

    # Controlla se la registrazione esiste già
    existing_registration = Registrazione.query.filter_by(
        user_id=userId,
        event_id=eventId
    ).first()

    if existing_registration:
        raise GraphQLError("L'utente è già registrato a questo evento")

    # Se non esiste, crea la nuova registrazione
    registration = Registrazione(user_id=userId, event_id=eventId)
    db.session.add(registration)
    db.session.commit()

    return registration.to_dict()

# Mutazione per annullare la registrazione a un evento
@mutation.field("cancelRegistration")
def resolve_cancel_registration(_, info, registrationId):
    registration = Registrazione.query.get(registrationId)
    if not registration:
        return {
            "success": False,
            "message": "La registrazione è già stata annullata o non esiste."
        }

    db.session.delete(registration)
    db.session.commit()
    return {
        "success": True,
        "message": "Registrazione cancellata con successo."
    }


# Creazione dello schema GraphQL con Query e Mutation
schema = make_executable_schema(type_defs, query, mutation)

@app.route("/graphqlMutation", methods=["POST", "GET"])
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
