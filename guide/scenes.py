import inspect
import sys
import enum
import csv

from guide.alice import Request
from guide.responce_helpers import (button, image_gallery)
from guide.scenes_util import Scene
from guide import intents
from guide.state import STATE_REQUEST_KEY


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
        if intents.TELL_ABOUT in request.intents:
            return HowIs_start()

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


class HowIs_start(GlobalScene):

    @staticmethod
    def __get_info(id: str):
        with open('guide/persons.csv', mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile, delimiter=';')
            for row in reader:
                if row["id"] == id:
                    return row

    def reply(self, request: Request):

        persona = request.intents[intents.TELL_ABOUT]["slots"]["who"]["value"]
        previous = request["state"][STATE_REQUEST_KEY].get("scene", "")
        data = self.__get_info(persona)
        text = data["short"] + "\nПродолжим?"
        card = image_gallery(image_ids=data["gallery"].split(sep='|'))

        return self.make_response(text, card=card, state={"scene": "HowIs_end", "previous": previous})


class HowIs_end(GlobalScene):

    def handle_local_intents(self, request: Request):
        if intents.CONFIRM in request.intents:
            return eval(request["state"][STATE_REQUEST_KEY]["scene"])
        elif intents.REJECT in request.intents:
            return Welcome()


def _list_scenes():
    current_module = sys.modules[__name__]
    scenes = []
    for name, obj in inspect.getmembers(current_module):
        if inspect.isclass(obj) and issubclass(obj, Scene):
            scenes.append(obj)
    return scenes


SCENES = {scene.id(): scene for scene in _list_scenes()}

DEFAULT_SCENE = Welcome
