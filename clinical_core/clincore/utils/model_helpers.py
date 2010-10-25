from datetime import datetime
import uuid

def make_time():
    return datetime.utcnow()

def make_uuid():
    return uuid.uuid1().hex
