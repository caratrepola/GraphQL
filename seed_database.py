from datetime import datetime
from database import create_app, db
from models import User, Event, Registrazione


def seed_database():

    app = create_app()
    with app.app_context():

        db.drop_all()
        db.create_all()

        # Crea utenti di esempio
        users = [
            User(name="Mario Rossi", email="mario.rossi@example.com"),
            User(name="Luigi Verdi", email="luigi.verdi@example.com"),
            User(name="Anna Bianchi", email="anna.bianchi@example.com"),
            User(name="Giulia Neri", email="giulia.neri@example.com")
        ]

        # Crea eventi di esempio
        events = [
            Event(
                titolo="Workshop Python",
                descrizione="Workshop introduttivo a Python e Flask",
                data=datetime(2025, 4, 15, 10, 0),
                luogo="Milano, Via Roma 123"
            ),
            Event(
                titolo="Conferenza Web Development",
                descrizione="Conferenza sulle nuove tecnologie web",
                data=datetime(2025, 5, 20, 9, 30),
                luogo="Roma, Piazza Navona 1"
            ),
            Event(
                titolo="Meetup Database",
                descrizione="Incontro su SQLAlchemy e ORM",
                data=datetime(2025, 6, 10, 18, 0),
                luogo="Firenze, Viale dei Colli 45"
            )
        ]

        # Aggiungi tutti i record al database
        db.session.add_all(users)
        db.session.add_all(events)

        # Conferma le modifiche
        db.session.commit()

        # Recupera gli ID generati
        users = User.query.all()
        events = Event.query.all()

        # Crea registrazioni di esempio
        registrations = [
            Registrazione(user_id=users[0].id, event_id=events[0].id),  # Mario Rossi → Workshop Python
            Registrazione(user_id=users[1].id, event_id=events[1].id),  # Luigi Verdi → Conferenza Web
            Registrazione(user_id=users[2].id, event_id=events[0].id),  # Anna Bianchi → Workshop Python
            Registrazione(user_id=users[3].id, event_id=events[2].id),  # Giulia Neri → Meetup Database
            Registrazione(user_id=users[0].id, event_id=events[2].id),  # Mario Rossi → Meetup Database
        ]

        # Aggiungi registrazioni al database
        db.session.add_all(registrations)
        db.session.commit()

        print("Database popolato con successo!")


if __name__ == "__main__":
    seed_database()