class MailRepository:
    def send(
        self, sender: tuple[str | None, str], receiver: tuple[str | None, str], subject: str, text: str, reply_to: str | None
    ) -> None:
        raise NotImplementedError  # pragma: no cover
