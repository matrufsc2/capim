from flask import Flask, request
import os
from flask.helpers import make_response
import hashlib
from werkzeug.utils import import_string, cached_property


class LazyView(object):
    def __init__(self, import_name):
        self.__module__, self.__name__ = import_name.rsplit('.', 1)
        self.import_name = import_name

    @cached_property
    def view(self):
        return import_string(self.import_name)

    def __call__(self, *args, **kwargs):
        return self.view(*args, **kwargs)

app = Flask(__name__)


def url(url_rule, import_name, **options):
    view = LazyView('app.views.' + import_name)
    app.add_url_rule(url_rule, view_func=view, **options)


IN_DEV = "dev" in os.environ.get("SERVER_SOFTWARE", "").lower()

if not IN_DEV:
    import rollbar
    import rollbar.contrib.flask
    from flask import got_request_exception
    rollbar.init(
        'ba9bf3c858294e0882d57a243084e20d',
        'production',
        root=os.path.dirname(os.path.realpath(__file__)),
        allow_logging_basic_config=False,
        handler='gae'
    )

    got_request_exception.connect(rollbar.contrib.flask.report_exception, app)


@app.after_request
def cache_response(response):
    """
    Cache the response if possible

    :param response: The response generated by the controller
    :type response: ConditionalResponse
    :return:
    """
    response.freeze()
    if request.method == 'GET':
        response.headers["Cache-Control"] = "must-revalidate, post-check=0, pre-check=0"
        etag = hashlib.sha1(response.get_data()).hexdigest()
        if request.if_none_match and etag in request.if_none_match:
            return make_response("", 304, response.headers)
        response.set_etag(etag)
    return response

###############################################
# These URLs will be loaded lazily, on demand #
###############################################

# Favicon
url("/favicon.ico", "favicon.favicon")

# API Index
url("/api/", "api.api_index")

# Semesters
url("/api/semesters/", "semesters.get_semesters")
url("/api/semesters/<id_value>", "semesters.get_semester")

# Campus
url("/api/campi/", "campi.get_campi")
url("/api/campi/<id_value>", "campi.get_campus")

# Disciplines
url("/api/disciplines/", "disciplines.get_disciplines")
url("/api/disciplines/<id_value>", "disciplines.get_discipline")

# Teams
url("/api/teams/", "teams.get_teams")
url("/api/teams/<id_value>", "teams.get_team")

# Plans
url("/api/plans/", "plans.get_plans")
url("/api/plans/", "plans.create_plan", methods=["POST"])
url("/api/plans/<id_value>", "plans.update_plan", methods=["PUT"])
url("/api/plans/<id_value>", "plans.get_plan")

# Pages
url("/api/pages/", "pages.get_pages")
url("/api/pages/<slug>", "pages.get_page")

# Blog
#      - Categories
url("/api/categories/", "blog.get_categories")
url("/api/categories/<id_value>", "blog.get_categorie")

#      - Posts
url("/api/posts/", "blog.get_posts")
url("/api/posts/<id_value>", "blog.get_post")

#      - Feed
url("/blog/feed.<type>", "blog.get_blog_feed")


# Help
#      - Sections
url("/api/sections/", "help.get_sections")
url("/api/sections/<id_value>", "help.get_section")

#      - Questions Groups
url("/api/questions-groups/", "help.get_questions_groups")
url("/api/questions-groups/<id_value>", "help.get_question_group")

#      - Articles
url("/api/articles/", "help.get_articles")
url("/api/articles/<id_value>", "help.get_article")

# Users
url("/api/users/current", "users.get_current_user", methods=["GET"])
url("/api/users", "users.get_users", methods=["GET"])

# Prismic
url("/api/prismic_preview/", "prismic.prismic_preview")

# Secret Routes
url("/secret/update/", "secret.update", methods=["GET", "POST"])
url("/secret/clear_cache/", "secret.clear_cache", methods=["GET", "POST"])

# About
url("/sobre/", "about.about")

# Other Pages
url("/", "other_pages.index")
url("/<path:path>", "other_pages.page")

if __name__ == "__main__":
    app.run()