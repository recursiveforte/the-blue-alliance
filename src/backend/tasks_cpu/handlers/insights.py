from flask import Blueprint, make_response, render_template, request, url_for
from google.appengine.api import taskqueue
from werkzeug.wrappers import Response

from backend.common.helpers.insights_helper import InsightsHelper
from backend.common.manipulators.insight_manipulator import InsightManipulator
from backend.common.models.keys import Year


blueprint = Blueprint("insights", __name__)


@blueprint.route("/backend-tasks-b2/math/enqueue/insights/<kind>/<int:year>")
def enqueue_year_insights(kind: str, year: Year) -> Response:
    """
    Enqueues Insights calculation of a given kind for a given year
    """
    taskqueue.add(
        url=url_for("insights.do_year_insights", kind=kind, year=year),
        method="GET",
        target="py3-tasks-cpu",
        queue_name="default",
    )

    if (
        "X-Appengine-Taskname" not in request.headers
    ):  # Only write out if not in taskqueue
        return make_response(
            render_template("math/year_insights_enqueue.html", kind=kind, year=year)
        )

    return make_response("")


@blueprint.route("/backend-tasks-b2/math/do/insights/<kind>/<int:year>")
def do_year_insights(kind: str, year: Year) -> Response:
    """
    Calculates insights of a given kind for a given year.
    """
    insights = None
    if kind == "matches":
        insights = InsightsHelper.doMatchInsights(year)
    elif kind == "awards":
        insights = InsightsHelper.doAwardInsights(year)
    elif kind == "predictions":
        insights = InsightsHelper.doPredictionInsights(year)

    if insights is not None:
        InsightManipulator.createOrUpdate(insights)

    if (
        "X-Appengine-Taskname" not in request.headers
    ):  # Only write out if not in taskqueue
        return make_response(
            render_template("math/year_insights_do.html", kind=kind, insights=insights)
        )

    return make_response("")


@blueprint.route("/backend-tasks-b2/math/enqueue/overallinsights/<kind>")
def enqueue_overall_insights(kind: str) -> Response:
    """
    Enqueues Overall Insights calculation for a given kind.
    """
    taskqueue.add(
        url=url_for("insights.do_overall_insights", kind=kind),
        method="GET",
        target="py3-tasks-cpu",
        queue_name="default",
    )

    if (
        "X-Appengine-Taskname" not in request.headers
    ):  # Only write out if not in taskqueue
        return make_response(
            render_template("math/overall_insights_enqueue.html", kind=kind)
        )

    return make_response("")


@blueprint.route("/backend-tasks-b2/math/do/overallinsights/<kind>")
def do_overall_insights(kind: str) -> Response:
    """
    Calculates overall insights of a given kind.
    """
    insights = None
    if kind == "matches":
        insights = InsightsHelper.doOverallMatchInsights()
    elif kind == "awards":
        insights = InsightsHelper.doOverallAwardInsights()

    if insights is not None:
        InsightManipulator.createOrUpdate(insights)

    if (
        "X-Appengine-Taskname" not in request.headers
    ):  # Only write out if not in taskqueue
        return make_response(
            render_template(
                "math/overall_insights_do.html", kind=kind, insights=insights
            )
        )

    return make_response("")
