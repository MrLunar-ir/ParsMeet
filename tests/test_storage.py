import os
from ParsMeet.storage import Storage

def test_storage_set_get(tmp_path):
    path = os.path.join(tmp_path, "test.json")
    s = Storage(path)
    s.set("user1", "coins", 100)
    assert s.get("user1", "coins") == 100

def test_storage_increment(tmp_path):
    path = os.path.join(tmp_path, "test.json")
    s = Storage(path)
    s.set("user1", "coins", 10)
    result = s.increment("user1", "coins", 5)
    assert result == 15

def test_storage_delete(tmp_path):
    path = os.path.join(tmp_path, "test.json")
    s = Storage(path)
    s.set("user1", "coins", 100)
    s.delete("user1", "coins")
    assert s.get("user1", "coins") is None