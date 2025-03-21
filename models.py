
from database import db


# Definizione del modello User
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "email": self.email}


# Definizione del modello Event
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titolo = db.Column(db.String(100), nullable=False)
    descrizione = db.Column(db.Text, nullable=True)
    data = db.Column(db.DateTime, nullable=False)
    luogo = db.Column(db.String(150), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "titolo": self.titolo,
            "descrizione": self.descrizione,
            "data": self.data.isoformat(),
            "luogo": self.luogo,
            "partecipanti": [registrazione.user.to_dict() for registrazione in self.registrazioni]

        }


# Modello Registrazione (relazione tra User e Event)
class Registrazione(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey("event.id"), nullable=False)
    data_registrazione = db.Column(db.DateTime, default=db.func.current_timestamp())

    # Relazioni
    user = db.relationship("User", backref=db.backref("registrazioni", lazy=True))
    event = db.relationship("Event", backref=db.backref("registrazioni", lazy=True))

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "event_id": self.event_id,
            "data_registrazione": self.data_registrazione.isoformat(),
        }
