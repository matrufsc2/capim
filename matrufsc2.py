import json
import urllib
import urlparse
import time
from flask import Flask, request, g, got_request_exception
import os
import re
import urllib2
from flask.helpers import make_response
from flask.wrappers import Response, Request
from werkzeug.wrappers import ETagResponseMixin, ETagRequestMixin
from app.cache import get_from_cache, set_into_cache
from google.appengine.api import users
from google.appengine.api.urlfetch import fetch
from app import api
from app.json_serializer import JSONEncoder
from app.robot.robot import Robot
import hashlib, logging
from google.appengine.api import app_identity
import rollbar
import rollbar.contrib.flask

try:
    import cPickle as pickle
except ImportError:
    import pickle

app = Flask(__name__)

bots_re = re.compile("(baiduspider|twitterbot|facebookexternalhit|rogerbot|linkedinbot|embedly|quora link preview|showyoubot|outbrain|pinterest|slackbot)", re.IGNORECASE)
prerender_re = re.compile("Prerender", re.IGNORECASE)

IN_DEV = "dev" in os.environ.get("SERVER_SOFTWARE", "").lower()

CACHE_RESPONSE_KEY = "cache/response/%d/%s"

if not IN_DEV:
    rollbar.init(
        'ba9bf3c858294e0882d57a243084e20d',
        'production',
        root=os.path.dirname(os.path.realpath(__file__)),
        allow_logging_basic_config=False
    )

    got_request_exception.connect(rollbar.contrib.flask.report_exception, app)

logging = logging.getLogger("matrufsc2")

def can_prerender():
    prerender = False
    if request.args.has_key("_escaped_fragment_"):
        logging.debug("Pre-rendering because of _escaped_fragment_ parameter")
        prerender = True
    user_agent = request.user_agent.string
    if bots_re.search(user_agent):
        logging.debug("Pre-rendering because of user-agent")
        prerender = True
    if prerender_re.search(user_agent):
        logging.debug("Disabling Pre-rendering because of user-agent")
        prerender = False
    return prerender

@app.before_request
def return_cached():
    """
    Return the cached response if possible

    :param request: The request generated by the user
    :type request: ConditionalRequest
    :return:
    """
    if request.method == "GET" and not request.path.startswith("/api/") and not request.path.startswith("/secret/"):
        prerender = can_prerender()
        url_hash = hashlib.sha1(request.base_url).hexdigest()
        cache_key = CACHE_RESPONSE_KEY % (int(prerender), url_hash)
        logging.debug("Trying to get response from cache..")
        response = get_from_cache(cache_key)
        if response:
            logging.debug("Response found on cache :D")
            g.ignorePostMiddleware = True
            return response
        else:
            logging.debug("Response not found on cache :(")
            g.ignorePostMiddleware = False


@app.after_request
def cache_response(response):
    """
    Cache the response if possible

    :param response: The response generated by the controller
    :type response: ConditionalResponse
    :return:
    """
    if getattr(g, "ignorePostMiddleware", None):
        return response
    if request.method == "GET":
        if not request.path.startswith("/api/") and not request.path.startswith("/secret/"):
            response.headers["Cache-Control"] = "public; max-age=3600"
            response.headers["Pragma"] = "cache"
            prerender = can_prerender()
            url_hash = hashlib.sha1(request.base_url).hexdigest()
            cache_key = CACHE_RESPONSE_KEY % (int(prerender), url_hash)
            logging.debug("Saving Response into cache :D")
            set_into_cache(cache_key, response)
    else:
        response.headers["Cache-Control"] = "private"
        response.headers["Pragma"] = "no-cache"
    return response


@app.route("/api/")
def api_index():
    return "", 404


def serialize(result, status=200, headers=None):
    if headers is None:
        headers = {}
    headers.update({"Content-Type": "application/json"})
    if not result and not isinstance(result, list):
        return "", 404, headers
    response = make_response(json.dumps(result, cls=JSONEncoder, separators=(',', ':')), status, headers)
    return response

@app.route("/api/semesters/")
def get_semesters():
    result = api.get_semesters(request.args.copy())
    return serialize(result)


@app.route("/api/semesters/<id_value>/")
def get_semester(id_value):
    result = api.get_semester(id_value)
    return serialize(result)


@app.route("/api/campi/")
def get_campi():
    result = api.get_campi(request.args.copy())
    return serialize(result)


@app.route("/api/campi/<id_value>")
def get_campus(id_value):
    result = api.get_campus(id_value)
    return serialize(result)


@app.route("/api/disciplines/")
def get_disciplines():
    result = api.get_disciplines(request.args.copy())
    return serialize(result)


@app.route("/api/disciplines/<id_value>")
def get_discipline(id_value):
    result = api.get_discipline(id_value)
    return serialize(result)


@app.route("/api/teams/")
def get_teams():
    result = api.get_teams(request.args.copy())
    return serialize(result)

@app.route("/api/teams/<id_value>")
def get_team(id_value):
    result = api.get_team(id_value)
    return serialize(result)

@app.route("/api/plans/")
def get_plans():
    result = api.get_plans(request.args.copy())
    return serialize(result)

@app.route("/api/plans/", methods=["POST"])
def create_plan():
    try:
        request_body = request.get_data(as_text=True)
        request_body = json.loads(request_body)
        result = api.create_plan(request_body)
    except (ValueError, KeyError), e:
        print e
        result = None
    return serialize(result)

@app.route("/api/plans/<id_value>")
def get_plan(id_value):
    result = api.get_plan(id_value)
    return serialize(result)

@app.route("/api/plans/<id_value>", methods=['PUT'])
def update_plan(id_value):
    try:
        request_body = request.get_data(as_text=True)
        request_body = json.loads(request_body)
        result = api.update_plan(id_value, request_body)
    except (ValueError, KeyError):
        result = None
    return serialize(result)

@app.route("/api/users/current", methods=["GET"])
def current_user():
    is_authenticated = users.get_current_user() is not None
    login_url = None
    logout_url = None
    if is_authenticated:
        logout_url = users.create_logout_url("/")
    else:
        login_url = users.create_login_url("/")
    return serialize({
        "id": "current",
        "is_authenticated": is_authenticated,
        "login_url": login_url,
        "logout_url": logout_url
    })

@app.route("/api/users", methods=["GET"])
def get_users():
    is_authenticated = users.get_current_user() is not None
    login_url = None
    logout_url = None
    if is_authenticated:
        logout_url = users.create_logout_url("/")
    else:
        login_url = users.create_login_url("/")
    return serialize([{
        "id": "current",
        "is_authenticated": is_authenticated,
        "login_url": login_url,
        "logout_url": logout_url
    }])

@app.route("/api/short/", methods=["POST"])
def short():
    args = urlparse.parse_qs(request.get_data(as_text=True))
    status_session_keys = [
        "plan",
        "version"
    ]
    filtered_args = {}
    for key in status_session_keys:
        if args.has_key(key):
            filtered_args[key] = args[key]
    if len(filtered_args) >= 2:
        host = app_identity.get_default_version_hostname()
        if "127.0.0.1" in host:
            return "{}", 406, {"Content-Type": "application/json"}
        content = {
            "longUrl": "http://%s/?%s"%(host, urllib.urlencode(filtered_args, True))
        }
        logging.debug("Shortening '%s'", content["longUrl"])
        content = json.dumps(content)
        googl_api_key = "{{googl_api_key}}"
        if "googl_api_key" not in googl_api_key:
            googl_api_key = "?key=%s" % googl_api_key
        else:
            googl_api_key = ""
        req = urllib2.Request(
            "https://www.googleapis.com/urlshortener/v1/url%s"%googl_api_key,
            content,
            {
                "Content-Type": "application/json"
            }
        )
        handler = urllib2.urlopen(req)
        content = handler.read()
        content = json.loads(content)
        short_url = content["id"]
        return serialize({
            "shortUrl": short_url
        })
    else:
        return serialize({}, 406)

@app.route("/secret/update/", methods=["GET", "POST"])
def update():
    robot = Robot()
    fut = robot.run(request.get_data())
    """ :type: google.appengine.ext.ndb.Future """
    return fut.get_result()

@app.route("/secret/clear_cache/", methods=["GET"])
def clear_cache():
    start = time.time()
    robot = Robot()
    robot.clear_gcs_cache()
    robot.update_cache()
    logging.debug("Cleared and updated cache in %f seconds", time.time()-start)
    return "OK", 200, {}

@app.route("/")
@app.route("/sobre/")
def index():
    prerender = can_prerender()
    if prerender:
        if IN_DEV:
            prerender_url = "http://127.0.0.1:3000/%s" % request.url
            prerender_headers = {}
        else:
            prerender_url = "http://service.prerender.io/%s" % request.url
            prerender_headers = {"X-Prerender-Token": "{{prerender_token}}"}
        try:
            logging.debug("Fetching prerender...")
            handler = fetch(prerender_url, headers=prerender_headers, allow_truncated=False,
                            deadline=60, follow_redirects=False)
            content = handler.content
            logging.debug("Prerender returned %d bytes...", len(content))
        except:
            prerender = False
    if not prerender:
        if IN_DEV:
            filename = "frontend/views/index.html"
        else:
            filename = "frontend/views/index-optimize.html"
        arq = open(filename)
        content = arq.read()
        arq.close()
        logging.debug("Reading %d bytes from HTML file", len(content))
    logging.debug("Sending %d bytes", len(content))
    return content, 200, {"Content-Type": "text/html; charset=UTF-8"}


app.debug = IN_DEV

if __name__ == "__main__":
    app.run()
elif IN_DEV:
    from google.appengine.ext.appstats import recording

    app = recording.appstats_wsgi_middleware(app)
