from enum import Enum


class JobState(Enum):
    READY = 1
    RUNNING = 2
    FINISHED = 3
    BLOCKED = 4
    ERROR = 4
