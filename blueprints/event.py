from flask import Blueprint, Response
from flask.views import MethodView

from .util import class_route, json_response

blp = Blueprint('Event', __name__)


@class_route(blp, '/api/v1/incident-update/notification')
class EventReceived(MethodView):
    init_every_request = False

    response = json_response({'message': 'Event processed.', 'code': 200}, 200)

    def post(self) -> Response:
        return self.response
