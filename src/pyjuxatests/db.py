from pyjuxa import db


def test_connect():
    Session = db.connect()
    _ = Session()
