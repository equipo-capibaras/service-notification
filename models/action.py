from enum import StrEnum


class Action(StrEnum):
    CREATED = 'created'
    ESCALATED = 'escalated'
    CLOSED = 'closed'
