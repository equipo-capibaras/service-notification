from dependency_injector import providers
from dependency_injector.containers import DeclarativeContainer, WiringConfiguration

from repositories.rest import SendgridMailRepository


class Container(DeclarativeContainer):
    wiring_config = WiringConfiguration(packages=['blueprints'])
    config = providers.Configuration()

    mail_repo = providers.ThreadSafeSingleton(
        SendgridMailRepository,
        token_provider=config.sendgrid.token_provider,
        blocklist=config.sendgrid.blocklist,
    )
