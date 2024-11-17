from enum import StrEnum


class Action(StrEnum):
    CREATED = 'created'
    ESCALATED = 'escalated'
    CLOSED = 'closed'
    AI_RESPONSE = 'AI_response'
