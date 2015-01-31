import logging
import datetime, calendar
from google.appengine.ext import ndb

from app.repositories import CampusRepository, DisciplinesRepository, TeamsRepository, SemesterRepository, \
    PlansRepository
from app.decorators import cacheable, searchable
from app.models import Plan


__author__ = 'fernando'

logging = logging.getLogger("matrufsc2_api")

@cacheable(consider_only=[])
def get_semesters(filters):
    repository = SemesterRepository()
    if filters:
        return repository.find_by(filters).get_result()
    return repository.find_all().get_result()

@cacheable()
def get_semester(id_value):
    repository = SemesterRepository()
    return repository.find_by_id(id_value).get_result()

@cacheable(consider_only=["semester"])
def get_campi(filters):
    repository = CampusRepository()
    if filters:
        return repository.find_by(filters).get_result()
    return repository.find_all().get_result()

@cacheable()
def get_campus(id_value):
    repository = CampusRepository()
    return repository.find_by_id(id_value).get_result()

@searchable(
    lambda item: " - ".join([item['code'], item['name']]),
    prefix="matrufsc2-discipline-",
    consider_only=['campus']
)
@cacheable()
def get_disciplines(filters):
    repository = DisciplinesRepository()
    if filters:
        disciplines = repository.find_by(filters).get_result()
    else:
        disciplines = repository.find_all().get_result()
    for discipline in disciplines:
        discipline.teams = []
    return disciplines


@cacheable()
def get_discipline(id_value):
    repository = DisciplinesRepository()
    discipline = repository.find_by_id(id_value).get_result()
    if discipline:
        discipline.teams = []
    return discipline

@cacheable(consider_only=["discipline"])
def get_teams(filters):
    repository = TeamsRepository()
    if filters:
        return repository.find_by(filters).get_result()
    return repository.find_all().get_result()


@cacheable()
def get_team(id_value):
    repository = TeamsRepository()
    return repository.find_by_id(id_value).get_result()


def get_plan(plan_id):
    repository = PlansRepository()
    return repository.find_by_id(plan_id).get_result()


def get_plans(data):
    if "code" not in data:
        return []
    code = Plan.generate_id_string(data["code"])
    result = []
    match = get_plan(code)
    if match:
        result.append(match)
    return result


@ndb.transactional
def create_plan(data):
    if "code" not in data or "data" not in data:
        return False
    code = data["code"]
    plan_id = Plan.generate_id_string(code)
    if get_plan(plan_id): # Check in cache AND in database
        return False
    model = Plan(
        key=ndb.Key(Plan, plan_id),
        code=code,
        history=[{
            "id": calendar.timegm(datetime.datetime.now().utctimetuple()),
            "data": data["data"]
        }]
    )
    model.put()
    return model


@ndb.transactional
def update_plan(plan_id, data):
    if "code" not in data or "data" not in data:
        return False
    plan_id_test = Plan.generate_id_string(data["code"])
    if plan_id_test != plan_id:
        return False
    model = get_plan(plan_id) # Get from cache if available
    # Get the UTC timestamp
    now = calendar.timegm(datetime.datetime.now().utctimetuple())
    # Identify possible duplicates:
    while True:
        found = False
        for item in model.history:
            if item["id"] == now:
                now += 1
                found = True
        if not found:
            break
    model.history.insert(0, {
        "id": now,
        "data": data["data"]
    })
    # Hard limit to history: 10 itens
    if len(model.history) > 10:
        model.history.pop()
    model.put()
    # Update cache too
    return model
