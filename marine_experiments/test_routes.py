"""Tests for the API routes."""

# pylint: skip-file

from unittest.mock import patch
from datetime import date, datetime

import pytest
from psycopg2 import connect


class TestExperimentGetRoute_Task_8:
    """Tests for the GET /experiment route."""

    def test_returns_200_on_GET(self, test_api):
        """Checks that the route accepts a GET request."""

        res = test_api.get("/experiment")

        assert res.status_code == 200

    def test_rejects_put_delete_calls(self, test_api):
        """Checks that the route does not accept invalid types of HTTP request."""

        assert test_api.delete("/experiment").status_code == 405
        assert test_api.put("/experiment").status_code == 405

    def test_returns_list_of_valid_dicts(self, test_api):
        """Checks that the route returns data in the right format."""

        res = test_api.get("/experiment")

        required_keys = ["experiment_date", "experiment_id",
                         "experiment_type", "score",
                         "species", "subject_id"]

        data = res.json

        assert isinstance(data, list), "Not a list"
        assert all(isinstance(d, dict) for d in data), "Not a list of dicts"
        assert all(len(d.keys()) == len(required_keys)
                   for d in data), "Wrong number of keys"
        for k in required_keys:
            assert all(k in d for d in data), f"Key ({k}) not found in data"

    def test_returns_data_in_expected_order(self, test_api):
        """Checks that experiments are returned in descending order by experiment_date."""

        res = test_api.get("/experiment")

        data = res.json

        dates = [datetime.strptime(experiment["experiment_date"], "%Y-%m-%d").date()
                 for experiment in data]

        for i in range(len(dates) - 1):
            assert dates[i] >= dates[i + 1], "Experiments out of order!"

    def test_returns_data_with_expected_types(self, test_api):
        """Checks that the returned data has the expected types."""

        res = test_api.get("/experiment")

        data = res.json

        for experiment in data:

            for k, v in experiment.items():
                if k not in ("subject_id", "experiment_id"):
                    assert isinstance(v, str)
                else:
                    assert isinstance(v, int)

    def test_returns_correctly_formatted_scores(self, test_api):
        """Checks that scores are returned in the expected format."""

        res = test_api.get("/experiment")

        data = res.json

        scores = [float(e["score"])
                  for e in data]

        assert all([
            0 <= s <= 100
            and round(s, 2) == s
            for s in scores
        ])

    def test_returns_expected_data(self, test_api, example_experiments):
        """Checks that the expected data is returned."""

        res = test_api.get("/experiment")

        data = res.json

        assert len(data) == 10

        for i in range(len(data)):
            assert data[i] == example_experiments[i]

    def test_returns_empty_list_if_no_subjects(self, test_api, test_temp_conn):
        """Checks that the response is an empty list if the database table is empty."""

        with test_temp_conn.cursor() as cur:
            cur.execute("TRUNCATE TABLE experiment CASCADE;")
            test_temp_conn.commit()

        res = test_api.get("/experiment")

        data = res.json

        assert isinstance(data, list)
        assert len(data) == 0

    def test_returns_all_experiments_by_default(self, test_api, test_temp_conn):
        """Checks that the response contains as many items as the database table."""

        with test_temp_conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS total FROM experiment;")
            total = cur.fetchone()["total"]

        res = test_api.get("/experiment")

        data = res.json

        assert isinstance(data, list)
        assert len(data) == total


class TestExperimentRoute_Task_9:
    """Tests for the /experiment route with parameters."""

    @pytest.mark.parametrize("filter_type", ("intelligance", 3, True, None, "agression"))
    def test_rejects_invalid_type_parameter(self, filter_type, test_api):
        """Checks that the route only accepts specific values"""
        res = test_api.get(f"/experiment?type={filter_type}")

        assert res.status_code == 400
        assert res.json == {"error": "Invalid value for 'type' parameter"}

    @pytest.mark.parametrize("filter_score", ("three", -17, 1010, 2.34))
    def test_rejects_invalid_score_over_parameter(self, filter_score, test_api):
        """Checks that the route only accepts specific values"""
        res = test_api.get(f"/experiment?score_over={filter_score}")

        assert res.status_code == 400
        assert res.json == {
            "error": "Invalid value for 'score_over' parameter"}

    @pytest.mark.parametrize("filter_score,output", ((90, 2), (80, 4), (50, 7), (1, 10)))
    def test_returns_expected_data_when_score_is_filtered(self, filter_score, output, test_api):
        """Checks that non-matching values are filtered out."""

        res = test_api.get(f"/experiment?score_over={filter_score}")

        data = res.json

        assert len(data) == output

        for d in data:
            assert float(d["score"][:-1]) >= filter_score

    @pytest.mark.parametrize("filter_type,output", (("intelligence", 5), ("obedience", 3), ("aggression", 2)))
    def test_returns_expected_data_when_type_is_filtered(self, filter_type, output, test_api):
        """Checks that non-matching values are filtered out."""

        res = test_api.get(f"/experiment?type={filter_type}")

        data = res.json

        assert len(data) == output

        for d in data:
            assert d["experiment_type"] == filter_type

    @pytest.mark.parametrize("filter_type,output", (("Intelligence", 5), ("oBeDiEnCe", 3), ("aGGressioN", 2)))
    def test_returns_expected_data_when_type_is_filtered_not_case_sensitive(self, filter_type, output, test_api):
        """Checks that non-matching values are filtered out."""

        res = test_api.get(f"/experiment?type={filter_type}")

        data = res.json

        assert len(data) == output

        for d in data:
            assert d["experiment_type"] == filter_type.lower()

    @pytest.mark.parametrize("filter_type, filter_score,output", (("obedience", 90, 0), ("intelligence", 50, 4), ("aggression", 2, 2)))
    def test_returns_expected_data_when_type_and_score_filtered(self, filter_type, filter_score, output, test_api):
        """Checks that non-matching values are filtered out."""

        res = test_api.get(
            f"/experiment?type={filter_type}&score_over={filter_score}")

        data = res.json

        assert len(data) == output

        for d in data:
            assert d["experiment_type"] == filter_type
            assert float(d["score"][:-1]) >= filter_score


class TestExperimentIDDeleteRoute_Task_10:
    """Tests for the /experiment/<id> route."""

    def test_returns_200_on_DELETE(self, test_api):
        """Checks that the route accepts a DELETE request."""

        res = test_api.delete("/experiment/3")

        assert res.status_code == 200

    def test_rejects_put_post_calls(self, test_api):
        """Checks that the route does not accept invalid types of HTTP request."""

        assert test_api.put("/experiment/3").status_code == 405
        assert test_api.post("/experiment/3").status_code == 405

    @pytest.mark.parametrize("id", (3000, 26, 9241))
    def test_rejects_invalid_id(self, id, test_api):
        """Checks that the route rejects an invalid ID."""

        print(f"/experiment/{id}")
        res = test_api.delete(f"/experiment/{id}")

        data = res.json

        assert res.status_code == 404
        assert isinstance(data, dict)

    def test_returns_data_in_expected_format(self, test_api):
        """Checks that the route returns JSON data in the required format."""

        res = test_api.delete("/experiment/3")

        data = res.json

        assert isinstance(data, dict)
        assert "experiment_id" in data
        assert "experiment_date" in data

    def test_returns_expected_data_types(self, test_api):
        """Checks that the route returns data with expected types/format."""

        res = test_api.delete("/experiment/2")

        data = res.json

        assert isinstance(data["experiment_id"], int)
        assert data["experiment_id"] == 2
        assert isinstance(data["experiment_date"], str)
        assert datetime.strptime(data["experiment_date"], "%Y-%m-%d")

    @pytest.mark.parametrize("id, exp_date", ((1, "2024-01-06"), (3, "2024-01-06"), (5, "2024-01-06")))
    def test_deletes_on_valid_id(self, id, exp_date, test_api, test_temp_conn):
        """Checks that the route deletes valid IDs."""

        res = test_api.delete(f"/experiment/{id}")
        data = res.json

        assert res.status_code == 200
        assert isinstance(data, dict)
        assert "experiment_id" in data
        assert "experiment_date" in data
        assert exp_date == data["experiment_date"]

        with test_temp_conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM experiment WHERE experiment_id = %s", [id])
            data = cur.fetchall()

        assert not data, "Failed to actually delete the row"
