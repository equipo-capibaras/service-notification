import os

from flask import Flask
from gcp_microservice_utils import setup_apigateway, setup_cloud_logging, setup_cloud_trace

from blueprints import BlueprintEvent, BlueprintHealth
from containers import Container


class FlaskMicroservice(Flask):
    container: Container


def create_app() -> FlaskMicroservice:
    if os.getenv('ENABLE_CLOUD_LOGGING') == '1':
        setup_cloud_logging()  # pragma: no cover

    app = FlaskMicroservice(__name__)
    app.container = Container()

    if os.getenv('ENABLE_CLOUD_TRACE') == '1':  # pragma: no cover
        setup_cloud_trace(app)

    setup_apigateway(app)

    if 'SENDGRID_APIKEY' in os.environ:  # pragma: no cover
        app.container.config.sendgrid.token_provider.from_value(
            type('TokenProvider', (object,), {'get_token': lambda: os.environ['SENDGRID_APIKEY']})
        )

    app.register_blueprint(BlueprintEvent)
    app.register_blueprint(BlueprintHealth)

    return app
