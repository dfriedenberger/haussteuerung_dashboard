from enum import Enum


class EventType(Enum):
    START = 0
    STOP = 1
    CYCLE = 2
    COMMAND = 3
    LOG = 4
    VALUE = 5
    VALUE_CHANGED = 6
    ALARM = 7
    ALARM_ACKNOWLEDGE = 8
