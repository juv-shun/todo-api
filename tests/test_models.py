import pytest

from app.models import ToDoTaskModel


@pytest.mark.asyncio
@pytest.mark.usefixtures("init_db")
class TestToDoTaskModel:

    create_patterns = {
        "normal pattern": (
            ToDoTaskModel("title7", "content7", "user1"),
            [7, "title7", "content7", "user1"],
            None,
        ),
        "content is None": (
            ToDoTaskModel("title8", None, "user1"),
            [8, "title8", None, "user1"],
            None,
        ),
        "id is set in advance": (
            ToDoTaskModel("title9", None, "user1", id=9),
            None,
            ValueError,
        ),
    }

    @pytest.mark.parametrize(
        "task, expected, error",
        list(create_patterns.values()),
        ids=list(create_patterns.keys()),
    )
    async def test_create(self, db_conn, task, expected, error):
        if error:
            with pytest.raises(error):
                await task.create(db_conn)
            return
        await task.create(db_conn)
        assert task.id == expected[0]
        row = await db_conn.fetchrow(
            "SELECT id, title, content, username FROM tasks WHERE id = $1", task.id
        )
        row = list(row) if row else None
        assert row == expected

    update_patterns = {
        "normal pattern": (
            ToDoTaskModel("title2-1", "content2-1", "shun", id=2),
            [2, "title2-1", "content2-1", "shun"],
            None,
        ),
        "content is None": (
            ToDoTaskModel("title1-1", None, "shun", id=1),
            [1, "title1-1", None, "shun"],
            None,
        ),
        "non-exist id specified": (
            ToDoTaskModel("title9999", "content9999", "dummyuser", id=9999),
            None,
            None,
        ),
        "username is different": (
            ToDoTaskModel("title3-1", "content3-1", "dummyuser", id=3),
            [3, "title3", None, "shun"],
            None,
        ),
        "model does not have id attr": (
            ToDoTaskModel("title1", None, "shun"),
            None,
            ValueError,
        ),
    }

    @pytest.mark.parametrize(
        "task, expected, error",
        list(update_patterns.values()),
        ids=list(update_patterns.keys()),
    )
    async def test_update(self, db_conn, task, expected, error):
        if error:
            with pytest.raises(error):
                await task.update(db_conn)
            return
        await task.update(db_conn)
        row = await db_conn.fetchrow(
            "SELECT id, title, content, username FROM tasks WHERE id = $1", task.id
        )
        row = list(row) if row else None
        assert row == expected

    delete_patterns = {
        "normal pattern": (
            ToDoTaskModel("title2", "", "shun", id=2),
            None,
            None,
        ),
        "non-exist id specified": (
            ToDoTaskModel("title9999", "content9999", "dummyuser", id=9999),
            None,
            None,
        ),
        "username is different": (
            ToDoTaskModel("title3", None, "dummyuser", id=3),
            [3, "title3", None, "shun"],
            None,
        ),
        "model does not have id attr": (
            ToDoTaskModel("title1", None, "shun"),
            None,
            ValueError,
        ),
    }

    @pytest.mark.parametrize(
        "task, expected, error",
        list(delete_patterns.values()),
        ids=list(delete_patterns.keys()),
    )
    async def test_delete(self, db_conn, task, expected, error):
        if error:
            with pytest.raises(error):
                await task.delete(db_conn)
            return
        await task.delete(db_conn)
        row = await db_conn.fetchrow(
            "SELECT id, title, content, username FROM tasks WHERE id = $1", task.id
        )
        row = list(row) if row else None
        assert row == expected

    get_patterns = {
        "normal pattern": (
            4,
            "dummyuser",
            ToDoTaskModel("title4", "content4", "dummyuser", id=4),
        ),
        "non-exist id specified": (9999, "shun", None),
        "username is different": (4, "foo", None),
    }

    @pytest.mark.parametrize(
        "id, user, expected", list(get_patterns.values()), ids=list(get_patterns.keys())
    )
    async def test_get(self, db_conn, id, user, expected):
        task = await ToDoTaskModel.get(db_conn, id, user)
        if isinstance(expected, ToDoTaskModel):
            assert task.__dict__ == expected.__dict__
        else:
            assert task == expected
