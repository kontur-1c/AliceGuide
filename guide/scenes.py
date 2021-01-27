import inspect
import sys
import enum

from guide.alice import Request
from guide.responce_helpers import button
from guide.scenes_util import Scene
from guide import intents


class QuestionType(enum.Enum):
    UNKNOWN = 1
    SIMPLE = 2
    HARD = 3
    ATTENTION = 4

    @classmethod
    def from_request(cls, request: Request, intent_name: str):
        slot = request.intents[intent_name]["slots"]["question_type"]["value"]
        if slot == "simple":
            return cls.SIMPLE
        elif slot == "hard":
            return cls.HARD
        elif slot == "attention":
            return cls.ATTENTION
        else:
            return cls.UNKNOWN


class GlobalScene(Scene):
    def reply(self, request: Request):
        pass

    def handle_global_intents(self, request):
        return HowIs()

    def handle_local_intents(self, request: Request):
        pass


class Welcome(GlobalScene):
    def reply(self, request: Request):
        text = (
            "Я могу провести экскурсию по памятнику "
            "могу рассказать, про каждую фигуру на памятнике "
            "а можем сыграть в викторину"
        )
        return self.make_response(
            text,
            buttons=[
                button("Сыграть в викторину"),
                button("Расскажи экскурсию"),
            ],
        )

    def handle_local_intents(self, request: Request):
        if intents.START_TOUR in request.intents:
            return StartTour()
        elif intents.START_GAME in request.intents:
            return StartGame()


class StartTour(GlobalScene):
    def reply(self, request: Request):
        text = "Наша экскурсия начинается с ..."  # TODO сценарий "Экскурсия"
        return self.make_response(text)

    def handle_local_intents(self, request: Request):
        pass


class StartGame(GlobalScene):
    def reply(self, request: Request):
        text = (
            "Вопросы бывают простые, сложные и на внимательность. "
            "Начнем с простого вопроса?"
        )
        return self.make_response(
            text,
            state={"screen": "start_tour"},
            buttons=[
                button("Простой"),
                button("Сложный"),
                button("На внимательность"),
            ],
        )

    def handle_local_intents(self, request: Request):
        if intents.GAME_QUESTION:
            question_type = QuestionType.from_request(request, intents.GAME_QUESTION)
            if question_type == QuestionType.SIMPLE:
                return SimpleQuestion()
            elif question_type == QuestionType.HARD:
                ...
            elif question_type == QuestionType.ATTENTION:
                ...


class SimpleQuestion(GlobalScene):
    def reply(self, request: Request):
        text = "Задаю простой вопрос..."  # TODO "Обработка вопросов"
        return self.make_response(text)

    def handle_local_intents(self, request: Request):
        pass


class HowIs(GlobalScene):
    def reply(self, request: Request):
        text = "Вы хотите узнать кто такой ..."
        return self.make_response(text)


def _list_scenes():
    current_module = sys.modules[__name__]
    scenes = []
    for name, obj in inspect.getmembers(current_module):
        if inspect.isclass(obj) and issubclass(obj, Scene):
            scenes.append(obj)
    return scenes


SCENES = {scene.id(): scene for scene in _list_scenes()}

DEFAULT_SCENE = Welcome
