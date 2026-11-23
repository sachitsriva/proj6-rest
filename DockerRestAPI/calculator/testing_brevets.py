from unittest.mock import patch
import flask_brevets


def test_submit():
    client = flask_brevets.app.test_client()
    control = {
        "km": "100",
        "location": "Checkpoint",
        "open": "Fri 11/13 10:56 UTC",
        "close": "Fri 11/13 14:40 UTC",
    }

    with patch.object(flask_brevets, "collection") as collection:
        response = client.post("/submit", json={"controls": [control]})

        assert response.status_code == 201
        collection.insert_one.assert_called_once_with({
            "controls": [{
                "km": 100.0,
                "location": "Checkpoint",
                "open": "Fri 11/13 10:56 UTC",
                "close": "Fri 11/13 14:40 UTC",
            }]
        })


def test_empty_submit():
    client = flask_brevets.app.test_client()

    with patch.object(flask_brevets, "collection") as collection:
        response = client.post("/submit", json={"controls": []})

        assert response.status_code == 400
        collection.insert_one.assert_not_called()


def test_display():
    client = flask_brevets.app.test_client()
    control = {
        "km": 100,
        "location": "Checkpoint",
        "open": "Fri 11/13 10:56 UTC",
        "close": "Fri 11/13 14:40 UTC",
    }

    with patch.object(flask_brevets, "collection") as collection:
        collection.find.return_value = [{"controls": [control]}]
        response = client.get("/display")

        assert response.status_code == 200
        assert b"Checkpoint" in response.data
        assert b"Fri 11/13 10:56 UTC" in response.data
        assert b"Fri 11/13 14:40 UTC" in response.data
        collection.find.assert_called_once()


def test_empty_display():
    client = flask_brevets.app.test_client()

    with patch.object(flask_brevets, "collection") as collection:
        collection.find.return_value = []
        response = client.get("/display")

        assert response.status_code == 200
        assert b"No controls have been submitted yet." in response.data


if __name__ == "__main__":
    test_submit()
    test_empty_submit()
    test_display()
    test_empty_display()
    print("All 4 tests passed.")