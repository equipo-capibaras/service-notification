from flask import Blueprint, Response
from flask.views import MethodView

from .util import class_route, json_response

blp = Blueprint('Health Check', __name__)


@class_route(blp, '/api/v1/health/notification')
class HealthCheck(MethodView):
    init_every_request = False

    def get(self) -> Response:
        return json_response({'status': 'Ok'}, 200)
