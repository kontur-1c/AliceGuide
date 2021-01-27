from abc import ABC, abstractmethod
from typing import Optional

from guide.alice import Request


class Scene(ABC):
    @classmethod
    def id(cls):
        return cls.__name__

    """Генерация ответа сцены"""

    @abstractmethod
    def reply(self, request):
        raise NotImplementedError()

    """Проверка перехода к новой сцене"""

    def move(self, request: Request):
        next_scene = self.handle_local_intents(request)
        if next_scene is None:
            next_scene = self.handle_global_intents(request)
        return next_scene

    @abstractmethod
    def handle_global_intents(self):
        raise NotImplementedError()

    @abstractmethod
    def handle_local_intents(request: Request) -> Optional[str]:
        raise NotImplementedError()

    def fallback(self, request: Request):
        return self.make_response(
            "Извините, я вас не поняла. Пожалуйста, попробуйте переформулировать вопрос."
        )

    def make_response(
        self, text, tts=None, card=None, state=None, buttons=None, directives=None
    ):
        response = {
            "text": text,
            "tts": tts if tts is not None else text,
        }
        if card is not None:
            response["card"] = card
        if buttons is not None:
            response["buttons"] = buttons
        if directives is not None:
            response["directives"] = directives
        webhook_response = {
            "response": response,
            "version": "1.0",
            STATE_RESPONSE_KEY: {
                "scene": self.id(),
            },
        }
        if state is not None:
            webhook_response[STATE_RESPONSE_KEY].update(state)
        return webhook_response


STATE_RESPONSE_KEY = "session_state"
