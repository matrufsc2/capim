import hashlib
from google.appengine.api import users
from app.json_serializer import JSONSerializable
from google.appengine.ext import ndb


class Semester(ndb.Model, JSONSerializable):
    name = ndb.StringProperty(indexed=False)
    campi = ndb.KeyProperty(kind="Campus", repeated=True, indexed=False)

    @property
    def id(self):
        return self.key.id()

    def to_json(self):
        return {
            "id": self.id,
            "name": self.name
        }


class Campus(ndb.Model, JSONSerializable):
    name = ndb.StringProperty(indexed=False)
    disciplines = ndb.KeyProperty(kind="Discipline", repeated=True, indexed=False)

    @property
    def id(self):
        return self.key.id()

    def to_json(self):
        return {
            "id": self.id,
            "name": self.name
        }

class Discipline(ndb.Model, JSONSerializable):
    code = ndb.StringProperty(indexed=False)
    name = ndb.StringProperty(indexed=False)
    teams = ndb.KeyProperty(kind="Team", repeated=True, indexed=False)

    @property
    def id(self):
        return self.key.id()

    def to_json(self):
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name
        }

class Team(ndb.Model, JSONSerializable):
    code = ndb.StringProperty(indexed=False)
    vacancies_offered = ndb.IntegerProperty(indexed=False)
    vacancies_filled = ndb.IntegerProperty(indexed=False)
    schedules = ndb.KeyProperty(kind="Schedule", repeated=True, indexed=False)
    teachers = ndb.KeyProperty(kind="Teacher", repeated=True, indexed=False)

    @property
    def id(self):
        return self.key.id()

    def to_json(self):
        return {
            "id": self.id,
            "code": self.code,
            "vacancies_offered": self.vacancies_offered,
            "vacancies_filled": self.vacancies_filled,
            "schedules": ndb.get_multi(self.schedules),
            "teachers": ndb.get_multi(self.teachers)
        }

class Teacher(ndb.Model, JSONSerializable):
    name = ndb.StringProperty(indexed=False)

    @property
    def id(self):
        return self.key.id()

    def to_json(self):
        return {
            "id": self.id,
            "name": self.name
        }


class Schedule(ndb.Model, JSONSerializable):
    hourStart = ndb.IntegerProperty(indexed=False)
    minuteStart = ndb.IntegerProperty(indexed=False)
    numberOfLessons = ndb.IntegerProperty(indexed=False)
    dayOfWeek = ndb.IntegerProperty(indexed=False)
    room = ndb.StringProperty(indexed=False)

    @property
    def id(self):
        return self.key.id()

    def to_json(self):
        return {
            "id": self.id,
            "hourStart": self.hourStart,
            "minuteStart": self.minuteStart,
            "numberOfLessons": self.numberOfLessons,
            "dayOfWeek": self.dayOfWeek,
            "room": self.room
        }


class Plan(ndb.Model, JSONSerializable):
    code = ndb.StringProperty(indexed=False)
    history = ndb.JsonProperty(indexed=False, compressed=True)

    @property
    def id(self):
        return self.key.id()

    def to_json(self):
        history = self.history
        return {
            "id": self.id,
            "code": self.code,
            "history": history,
            "data": history[0]["data"]
        }

    @staticmethod
    def generate_id_string(code):
        user = users.get_current_user()
        if user:
            user = user.user_id()
        hash_code = "matrufsc2-plan-%s"%hashlib.sha1("-".join([code, str(user)])).hexdigest()
        return hash_code
