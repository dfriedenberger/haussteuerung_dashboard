from enum import Enum


class EventType(Enum):
    START = 0
    STOP = 1
    CYCLE = 2
    COMMAND = 3
    LOG = 4
    VALUE = 5
    ALARM = 6
