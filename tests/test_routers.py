import re
from typing import Any, Dict

import pytest

from starlette.testclient import TestClient

from src.main import app
from src.auth import get_current_user


# mock up cognito authentication
def mock_cognito_user():
    class MockUser:
        def __init__(self, username):
            self.username = username

    return MockUser("shun")


app.dependency_overrides[get_current_user] = mock_cognito_user


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as client:
        yield client


class TestCreateTask:
    patterns_201 = {
        "normal request": {
            "headers": {"content-type": "application/json"},
            "body": {"title": "a" * 100, "content": "a" * 1000},
        },
        "content key nothing": {
            "headers": {"content-type": "application/json"},
            "body": {"title": "a" * 100},
        },
        "content key empty": {
            "headers": {"content-type": "application/json"},
            "body": {"title": "a" * 100, "content": ""},
        },
        "content-type header key nothing": {
            "headers": {},
            "body": {"title": "a" * 100, "content": "a" * 1000},
        },
        "title and content are not string, but ok": {
            "headers": {},
            "body": {"title": 1, "content": False},
        },
    }

    @pytest.mark.parametrize(
        "req", list(patterns_201.values()), ids=list(patterns_201.keys())
    )
    def test_create_201(
        self,
        client: TestClient,
        req: Dict[str, Any],
    ):
        actual = client.post(url="/v1/task", headers=req["headers"], json=req["body"])
        assert actual.status_code == 201
        assert actual.json() is None
        assert re.match(r"^http://.*/task/\d+$", actual.headers["location"]) is not None

    patterns_422 = {
        "title key nothing": (
            {
                "headers": {"content-type": "application/json"},
                "body": {"content": "a" * 1000},
            },
            {
                "body": {
                    "detail": [
                        {
                            "loc": ["body", "title"],
                            "msg": "field required",
                            "type": "value_error.missing",
                        }
                    ]
                }
            },
        ),
        "title value empty": (
            {
                "headers": {"content-type": "application/json"},
                "body": {"title": "", "content": "a" * 1000},
            },
            {
                "body": {
                    "detail": [
                        {
                            "loc": ["body", "title"],
                            "msg": "ensure this value has at least 1 characters",
                            "type": "value_error.any_str.min_length",
                            "ctx": {"limit_value": 1},
                        }
                    ]
                }
            },
        ),
        "title value over max_length": (
            {
                "headers": {"content-type": "application/json"},
                "body": {"title": "a" * 101, "content": "a" * 1000},
            },
            {
                "body": {
                    "detail": [
                        {
                            "loc": ["body", "title"],
                            "msg": "ensure this value has at most 100 characters",
                            "type": "value_error.any_str.max_length",
                            "ctx": {"limit_value": 100},
                        }
                    ]
                }
            },
        ),
        "content value over max_length": (
            {
                "headers": {"content-type": "application/json"},
                "body": {"title": "a" * 100, "content": "a" * 1001},
            },
            {
                "body": {
                    "detail": [
                        {
                            "loc": ["body", "content"],
                            "msg": "ensure this value has at most 1000 characters",
                            "type": "value_error.any_str.max_length",
                            "ctx": {"limit_value": 1000},
                        }
                    ]
                }
            },
        ),
        "title is list object": (
            {
                "headers": {"content-type": "application/json"},
                "body": {"title": ["a"] * 10, "content": "a" * 1000},
            },
            {
                "body": {
                    "detail": [
                        {
                            "loc": ["body", "title"],
                            "msg": "str type expected",
                            "type": "type_error.str",
                        }
                    ],
                }
            },
        ),
        "content is dict object": (
            {
                "headers": {"content-type": "application/json"},
                "body": {"title": "a" * 100, "content": {"a": 1}},
            },
            {
                "body": {
                    "detail": [
                        {
                            "loc": ["body", "content"],
                            "msg": "str type expected",
                            "type": "type_error.str",
                        }
                    ],
                }
            },
        ),
    }

    @pytest.mark.parametrize(
        "req, expected", list(patterns_422.values()), ids=list(patterns_422.keys())
    )
    def test_create_422(
        self,
        client: TestClient,
        req: Dict[str, Any],
        expected: Dict[str, Any],
    ):
        actual = client.post(url="/v1/task", headers=req["headers"], json=req["body"])
        assert actual.status_code == 422
        assert actual.json() == expected["body"]


@pytest.mark.usefixtures("init_db")
class TestUpdateTask:
    patterns_200 = {
        name: dict(params, **{"path": {"id": 1}})
        for name, params in TestCreateTask.patterns_201.items()
    }

    @pytest.mark.parametrize(
        "req", list(patterns_200.values()), ids=list(patterns_200.keys())
    )
    def test_update_200(
        self,
        client: TestClient,
        req: Dict[str, Any],
    ):
        actual = client.put(
            url=f"/v1/task/{req['path']['id']}",
            headers=req["headers"],
            json=req["body"],
        )
        assert actual.status_code == 200
        assert actual.json() is None

    patterns_422 = {
        name: (dict(params[0], **{"path": {"id": 1}}), params[1])
        for name, params in TestCreateTask.patterns_422.items()
    }

    @pytest.mark.parametrize(
        "req, expected", list(patterns_422.values()), ids=list(patterns_422.keys())
    )
    def test_update_422(
        self,
        client: TestClient,
        req: Dict[str, Any],
        expected: Dict[str, Any],
    ):
        actual = client.put(
            url=f"/v1/task/{req['path']['id']}",
            headers=req["headers"],
            json=req["body"],
        )
        assert actual.status_code == 422
        assert actual.json() == expected["body"]

    patterns_404 = {
        "non-exist id": {
            "path": {"id": 9999},
            "headers": {"content-type": "application/json"},
            "body": {"title": "a" * 100, "content": "a" * 1000},
        },
        "exist id, but not users' id": {
            "path": {"id": 4},
            "headers": {"content-type": "application/json"},
            "body": {"title": "a" * 100, "content": "a" * 1000},
        },
    }

    @pytest.mark.parametrize(
        "req", list(patterns_404.values()), ids=list(patterns_404.keys())
    )
    def test_update_404(
        self,
        client: TestClient,
        req: Dict[str, Any],
    ):
        actual = client.put(
            url=f"/v1/task/{req['path']['id']}",
            headers=req["headers"],
            json=req["body"],
        )
        assert actual.status_code == 404
        assert actual.json() == {"detail": "Not Found"}


@pytest.mark.usefixtures("init_db")
class TestDeleteTask:
    patterns_200 = {
        "exist id": {
            "path": {"id": 1},
            "headers": {"content-type": "application/json"},
        }
    }

    @pytest.mark.parametrize(
        "req", list(patterns_200.values()), ids=list(patterns_200.keys())
    )
    def test_delete_200(
        self,
        client: TestClient,
        req: Dict[str, Any],
    ):
        actual = client.delete(
            url=f"/v1/task/{req['path']['id']}", headers=req["headers"]
        )
        assert actual.status_code == 200
        assert actual.json() is None

    patterns_404 = TestUpdateTask.patterns_404

    @pytest.mark.parametrize(
        "req", list(patterns_404.values()), ids=list(patterns_404.keys())
    )
    def test_delete_404(
        self,
        client: TestClient,
        req: Dict[str, Any],
    ):
        actual = client.delete(
            url=f"/v1/task/{req['path']['id']}", headers=req["headers"]
        )
        assert actual.status_code == 404
        assert actual.json() == {"detail": "Not Found"}


@pytest.mark.usefixtures("init_db")
class TestSearchTask:
    patterns_200 = {
        "normal pattern": (
            {
                "params": {"q": "title", "count": 2, "page": 1},
                "headers": {"content-type": "application/json"},
            },
            {
                "headers": {
                    "link": "<http://testserver/v1/task/_search?q=title"
                    + '&count=2&page=1?q=title&count=2&page=2>; rel="next"'
                },
                "body": [
                    {"content": None, "id": 3, "title": "title3"},
                    {"content": "", "id": 2, "title": "title2"},
                ],
            },
        ),
        "count key nothing": (
            {
                "params": {"q": "title", "page": 1},
                "headers": {"content-type": "application/json"},
            },
            {
                "headers": {"link": ""},
                "body": [
                    {"content": None, "id": 3, "title": "title3"},
                    {"content": "", "id": 2, "title": "title2"},
                    {"content": "content1", "id": 1, "title": "title1"},
                ],
            },
        ),
        "page key nothing": (
            {
                "params": {"q": "title", "count": 3},
                "headers": {"content-type": "application/json"},
            },
            {
                "headers": {"link": ""},
                "body": [
                    {"content": None, "id": 3, "title": "title3"},
                    {"content": "", "id": 2, "title": "title2"},
                    {"content": "content1", "id": 1, "title": "title1"},
                ],
            },
        ),
        "count key is maximum": (
            {
                "params": {"q": "title", "count": 100, "page": 1},
                "headers": {"content-type": "application/json"},
            },
            {
                "headers": {"link": ""},
                "body": [
                    {"content": None, "id": 3, "title": "title3"},
                    {"content": "", "id": 2, "title": "title2"},
                    {"content": "content1", "id": 1, "title": "title1"},
                ],
            },
        ),
        "page value is big": (
            {
                "params": {"q": "title", "count": 10, "page": 999999},
                "headers": {"content-type": "application/json"},
            },
            {
                "headers": {"link": ""},
                "body": [],
            },
        ),
        "q word does not match": (
            {
                "params": {"q": "foo", "count": 10, "page": 1},
                "headers": {"content-type": "application/json"},
            },
            {
                "headers": {"link": ""},
                "body": [],
            },
        ),
        "q word matches with content": (
            {
                "params": {"q": "content", "count": 10, "page": 1},
                "headers": {"content-type": "application/json"},
            },
            {
                "headers": {"link": ""},
                "body": [{"content": "content1", "id": 1, "title": "title1"}],
            },
        ),
    }

    @pytest.mark.parametrize(
        "req, expected",
        list(patterns_200.values()),
        ids=list(patterns_200.keys()),
    )
    def test_serach_200(
        self,
        client: TestClient,
        req: Dict[str, Any],
        expected: Dict[str, Any],
    ):
        actual = client.get(
            url="/v1/task/_search",
            headers={"content-type": "application/json"},
            params=req["params"],
        )
        assert actual.status_code == 200
        assert actual.json() == expected["body"]
        assert actual.headers["link"] == expected["headers"]["link"]

    patterns_422 = {
        "q key nothing": (
            {
                "params": {"count": 1, "page": 1},
                "headers": {"content-type": "application/json"},
            },
            {
                "body": {
                    "detail": [
                        {
                            "loc": ["query", "q"],
                            "msg": "field required",
                            "type": "value_error.missing",
                        }
                    ]
                },
            },
        ),
        "q is empty": (
            {
                "params": {"q": "", "count": 1, "page": 1},
                "headers": {"content-type": "application/json"},
            },
            {
                "body": {
                    "detail": [
                        {
                            "ctx": {"limit_value": 1},
                            "loc": ["query", "q"],
                            "msg": "ensure this value has at least 1 characters",
                            "type": "value_error.any_str.min_length",
                        }
                    ]
                },
            },
        ),
        "q is too long": (
            {
                "params": {"q": "a" * 101, "count": 1, "page": 1},
                "headers": {"content-type": "application/json"},
            },
            {
                "body": {
                    "detail": [
                        {
                            "ctx": {"limit_value": 100},
                            "loc": ["query", "q"],
                            "msg": "ensure this value has at most 100 characters",
                            "type": "value_error.any_str.max_length",
                        }
                    ]
                },
            },
        ),
        "count is not numeric": (
            {
                "params": {"q": "a", "count": "foo", "page": 1},
                "headers": {"content-type": "application/json"},
            },
            {
                "body": {
                    "detail": [
                        {
                            "loc": ["query", "count"],
                            "msg": "value is not a valid integer",
                            "type": "type_error.integer",
                        }
                    ]
                },
            },
        ),
        "count is less than 1": (
            {
                "params": {"q": "a", "count": 0, "page": 1},
                "headers": {"content-type": "application/json"},
            },
            {
                "body": {
                    "detail": [
                        {
                            "ctx": {"limit_value": 1},
                            "loc": ["query", "count"],
                            "msg": "ensure this value is greater than or equal to 1",
                            "type": "value_error.number.not_ge",
                        }
                    ]
                },
            },
        ),
        "count is greater than 100": (
            {
                "params": {"q": "a", "count": 101, "page": 1},
                "headers": {"content-type": "application/json"},
            },
            {
                "body": {
                    "detail": [
                        {
                            "ctx": {"limit_value": 100},
                            "loc": ["query", "count"],
                            "msg": "ensure this value is less than or equal to 100",
                            "type": "value_error.number.not_le",
                        }
                    ]
                },
            },
        ),
        "page is not numeric": (
            {
                "params": {"q": "a", "count": 100, "page": "foo"},
                "headers": {"content-type": "application/json"},
            },
            {
                "body": {
                    "detail": [
                        {
                            "loc": ["query", "page"],
                            "msg": "value is not a valid integer",
                            "type": "type_error.integer",
                        }
                    ]
                },
            },
        ),
        "page is less than 0": (
            {
                "params": {"q": "a", "count": 100, "page": 0},
                "headers": {"content-type": "application/json"},
            },
            {
                "body": {
                    "detail": [
                        {
                            "ctx": {"limit_value": 1},
                            "loc": ["query", "page"],
                            "msg": "ensure this value is greater than or equal to 1",
                            "type": "value_error.number.not_ge",
                        }
                    ]
                },
            },
        ),
    }

    @pytest.mark.parametrize(
        "req, expected", list(patterns_422.values()), ids=list(patterns_422.keys())
    )
    def test_serach_422(
        self,
        client: TestClient,
        req: Dict[str, Any],
        expected: Dict[str, Any],
    ):
        actual = client.get(
            url="/v1/task/_search", headers=req["headers"], params=req["params"]
        )
        assert actual.status_code == 422
        assert actual.json() == expected["body"]


@pytest.mark.usefixtures("init_db")
class TestGetTask:
    patterns_200 = {
        "exist id": (
            {"path": {"id": 1}, "headers": {"content-type": "application/json"}},
            {"body": {"id": 1, "title": "title1", "content": "content1"}},
        )
    }

    @pytest.mark.parametrize(
        "req, expected", list(patterns_200.values()), ids=list(patterns_200.keys())
    )
    def test_delete_200(
        self,
        client: TestClient,
        req: Dict[str, Any],
        expected: Dict[str, Any],
    ):
        actual = client.get(url=f"/v1/task/{req['path']['id']}", headers=req["headers"])
        assert actual.status_code == 200
        assert actual.json() == expected["body"]

    patterns_404 = TestUpdateTask.patterns_404

    @pytest.mark.parametrize(
        "req", list(patterns_404.values()), ids=list(patterns_404.keys())
    )
    def test_delete_404(
        self,
        client: TestClient,
        req: Dict[str, Any],
    ):
        actual = client.get(url=f"/v1/task/{req['path']['id']}", headers=req["headers"])
        assert actual.status_code == 404
        assert actual.json() == {"detail": "Not Found"}
