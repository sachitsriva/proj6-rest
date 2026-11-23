"""
Replacement for RUSA ACP brevet time calculator
(see https://rusa.org/octime_acp.html)

"""

from tracemalloc import start

import flask
from flask import request, Flask, jsonify, render_template, request
import arrow  # Replacement for datetime, based on moment.js
import acp_times  # Brevet time calculations
import config
import math
from pymongo import MongoClient
from pymongo.errors import PyMongoError
import secrets

import logging

###
# Globals
###
app = flask.Flask(__name__)
CONFIG = config.configuration()
app.secret_key = getattr(CONFIG, "SECRET_KEY", None) or secrets.token_hex(32)

client = MongoClient(
    "mongodb://db:27017/",
    serverSelectionTimeoutMS=3000
)
collection = client.brevets.controls

###
# Pages
###


@app.route("/")
@app.route("/index")
def index():
    app.logger.debug("Main page entry")
    return flask.render_template('calc.html')


@app.errorhandler(404)
def page_not_found(error):
    app.logger.debug("Page not found")
    flask.session['linkback'] = flask.url_for("index")
    return flask.render_template('404.html'), 404

###############
#
# AJAX request handlers
#   These return JSON, rather than rendering pages.
#
###############
@app.route("/_calc_times")
def _calc_times():
    """
    Calculates open/close times from miles, using rules
    described at https://rusa.org/octime_alg.html.
    Expects one URL-encoded argument, the number of miles.
    """
    km = request.args.get("km", type=float)
    brevet = request.args.get("brevet_dist_km", type=float)
    begin_date = request.args.get("begin_date", "")
    begin_time = request.args.get("begin_time", "")
    offset = request.args.get("utc_offset", "+00:00")

    if km is None or brevet is None:
        return "Enter valid distances", 400

    start = arrow.get(f"{begin_date}T{begin_time}{offset}").isoformat()

    opening = acp_times.open_time(km, brevet, start)
    closing = acp_times.close_time(km, brevet, start)
    result = {
        "open": opening,
        "close": closing,
    }

    return flask.jsonify(result=result)

@app.route("/submit", methods=["POST"])
def submit():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return flask.jsonify(error="Invalid submission."), 400

    controls = data.get("controls")

    if not isinstance(controls, list) or not controls:
        return flask.jsonify(
            error="Enter at least one control time before submitting."
        ), 400

    saved_controls = []

    for control in controls:
        if not isinstance(control, dict):
            return flask.jsonify(error="Invalid control entry."), 400

        try:
            km = float(control.get("km", ""))
        except (TypeError, ValueError):
            return flask.jsonify(
                error="Each control needs a valid distance."
            ), 400

        if not math.isfinite(km) or km < 0:
            return flask.jsonify(
                error="Distances must be nonnegative numbers."
            ), 400

        opening = control.get("open")
        closing = control.get("close")
        location = control.get("location", "")

        if (
            not isinstance(opening, str)
            or not opening.strip()
            or not isinstance(closing, str)
            or not closing.strip()
        ):
            return flask.jsonify(
                error="Each control needs calculated opening and closing times."
            ), 400

        if not isinstance(location, str):
            return flask.jsonify(error="Location must be text."), 400

        saved_control = {
            "km": km,
            "location": location,
            "open": opening,
            "close": closing,
        }

        for field in ("open_iso", "close_iso"):
            value = control.get(field)
            if isinstance(value, str) and value:
                saved_control[field] = value

        saved_controls.append(saved_control)

    try:
        collection.insert_one({"controls": saved_controls})
    except PyMongoError:
        return flask.jsonify(
            error="Could not save controls. Please try again."
        ), 503

    return flask.jsonify(
        message=f"Saved {len(saved_controls)} control(s)."
    ), 201


@app.route("/display")
def display():
    try:
        submissions = list(collection.find())
    except PyMongoError:
        return flask.render_template(
            "display.html",
            submissions=[],
            error="Could not load saved controls. Please try again."
        ), 503

    return flask.render_template(
        "display.html",
        submissions=submissions,
        error=None
    )

app.debug = CONFIG.DEBUG
if app.debug:
    app.logger.setLevel(logging.DEBUG)

if __name__ == "__main__":
    print("Opening for global access on port {}".format(CONFIG.PORT))
    app.run(port=CONFIG.PORT, host="0.0.0.0")
