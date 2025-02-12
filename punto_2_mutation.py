from flask import Flask, request, jsonify
from ariadne import gql, make_executable_schema, ObjectType, graphql_sync
import requests

API_ESTERNA = "https://external-app.com/api"

app = Flask(__name__)

# Definizione dello schema GraphQL
type_defs = gql("""
type User {
    id: ID!
    name: String!
    email: String!
}

type Event {
    id: ID!
    title: String!
    description: String!
}

type Registration {
    id: ID!
    user: User!
    event: Event!
}

type Mutation {
    createUser(name: String!, email: String!): User
    createEvent(title: String!, description: String!): Event
    updateUser(id: ID!, name: String, email: String): User
    registerUserToEvent(userId: ID!, eventId: ID!): Registration
    cancelRegistration(registrationId: ID!): Boolean
}
""")

mutation = ObjectType("Mutation")


# Mutazione per creare un nuovo utente
@mutation.field("createUser")
def resolve_create_user(_, info, name, email):
    response = requests.post(f"{API_ESTERNA}/users", json={"name": name, "email": email})
    return response.json() if response.status_code == 201 else {"error": "Impossibile creare l'utente"}


# Mutazione per creare un nuovo evento
@mutation.field("createEvent")
def resolve_create_event(_, info, title, description):
    response = requests.post(f"{API_ESTERNA}/events", json={"title": title, "description": description})
    return response.json() if response.status_code == 201 else {"error": "Impossibile creare l'evento"}


# Mutazione per aggiornare le informazioni di un utente esistente
@mutation.field("updateUser")
def resolve_update_user(_, info, id, name=None, email=None):
    data = {k: v for k, v in {"name": name, "email": email}.items() if v is not None}
    response = requests.put(f"{API_ESTERNA}/users/{id}", json=data)
    return response.json() if response.status_code == 200 else {"error": "Impossibile aggiornare l'utente"}


# Mutazione per registrare un utente a un evento
@mutation.field("registerUserToEvent")
def resolve_register_user_to_event(_, info, userId, eventId):
    response = requests.post(f"{API_ESTERNA}/registrations", json={"userId": userId, "eventId": eventId})
    return response.json() if response.status_code == 201 else {"error": "Impossibile registrare l'utente all'evento"}


# Mutazione per annullare la registrazione a un evento
@mutation.field("cancelRegistration")
def resolve_cancel_registration(_, info, registrationId):
    response = requests.delete(f"{API_ESTERNA}/registrations/{registrationId}")
    return response.status_code == 204


# Creazione dello schema GraphQL
schema = make_executable_schema(type_defs, mutation)


@app.route("/graphql", methods=["POST"])
def graphql_server():
    data = request.get_json()
    success, result = graphql_sync(schema, data, context_value=request, debug=True)
    status_code = 200 if success else 400
    return jsonify(result), status_code


if __name__ == "__main__":
    app.run(debug=True)
