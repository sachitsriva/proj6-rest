# Laptop Service

import csv
from datetime import datetime
from io import StringIO

from flask import Flask, Response, jsonify, request
from flask_restful import Api, Resource
from pymongo import MongoClient
from pymongo.errors import PyMongoError

app = Flask(__name__)
api = Api(app)

client = MongoClient("mongodb://db:27017/", serverSelectionTimeoutMS=3000)
collection = client.brevets.controls


class BrevetTimes(Resource):
    def get(self, representation="json"):
        fields = self.fields
        top = request.args.get("top")

        if top is not None:
            try:
                top = int(top)
                if top < 0:
                    raise ValueError
            except ValueError:
                return {"error": "top must be a nonnegative integer."}, 400

        try:
            rows = [
                {
                    field: control.get(f"{field}_iso") or control[field]
                    for field in fields
                }
                for submission in collection.find({}, {"controls": 1, "_id": 0})
                for control in submission["controls"]
            ]
        except PyMongoError:
            return {"error": "Could not load saved controls."}, 503

        if top is not None:
            sort_field = fields[0]
            try:
                rows.sort(key=lambda row: datetime.fromisoformat(row[sort_field]))
            except (TypeError, ValueError):
                return {"error": "Some saved controls lack sortable timestamps."}, 422
            rows = rows[:top]

        if representation == "csv":
            output = StringIO()
            writer = csv.DictWriter(output, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
            return Response(output.getvalue(), mimetype="text/csv")

        return jsonify(controls=rows)


class AllTimes(BrevetTimes):
    fields = ("open", "close")


class OpenTimes(BrevetTimes):
    fields = ("open",)


class CloseTimes(BrevetTimes):
    fields = ("close",)


api.add_resource(
    AllTimes,
    "/listAll",
    "/listAll/<any(json,csv):representation>",
)

api.add_resource(
    OpenTimes,
    "/listOpenOnly",
    "/listOpenOnly/<any(json,csv):representation>",
)

api.add_resource(
    CloseTimes,
    "/listCloseOnly",
    "/listCloseOnly/<any(json,csv):representation>",
)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)