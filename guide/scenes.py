import csv
import enum
import inspect
import random
import sys
from dataclasses import dataclass

from guide import intents
from guide.alice import Request
from guide.responce_helpers import button, image_gallery
from guide.scenes_util import Scene
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
            return WhoIs()

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
            buttons=[
                button("Простой"),
                button("Сложный"),
                button("На внимательность"),
            ],
        )

    def handle_local_intents(self, request: Request):
        if intents.GAME_QUESTION in request.intents:
            question_type = QuestionType.from_request(request, intents.GAME_QUESTION)
            if question_type == QuestionType.SIMPLE:
                return QuestionScene()
            elif question_type == QuestionType.HARD:
                ...
            elif question_type == QuestionType.ATTENTION:
                ...


@dataclass
class QuestionRecord:
    questiontype: QuestionType
    text: str
    # answer_type: ...
    answer: int
    # buttons: Optional[str]


questions_db = {
    1: QuestionRecord(
        QuestionType.SIMPLE,
        "Задаю простой вопрос. Какова общая высота памятника?",
        15,
    ),
    2: QuestionRecord(
        QuestionType.SIMPLE,
        (
            "Задаю сложный вопрос. Сколько поэтов,"
            "стихотворения которых изучают в школе, изображны на памятнике?"
        ),
        6,
    ),
    3: QuestionRecord(QuestionType.SIMPLE, "В чем смысл жизни", 42),
}


class QuestionScene(GlobalScene):
    def reply(self, request: Request):
        q = QuestionType.from_request(request, intents.GAME_QUESTION)
        text = ""
        if q == QuestionType.SIMPLE:
            q_id = random.choice(list(questions_db.keys()))
            q = questions_db[q_id]
            text = q.text
        elif q == QuestionType.HARD:
            text = "Задаю сложный вопрос..."
        elif q == QuestionType.ATTENTION:
            text = "Задаю вопрос на внимательность..."
        return self.make_response(text, state={"question_id": q_id})

    def handle_local_intents(self, request: Request):
        return AnswerScene()

    def handle_global_intents(self):
        pass


class AnswerScene(GlobalScene):
    def reply(self, request: Request):
        q_id = request.request_body["state"][STATE_REQUEST_KEY]["question_id"]
        q = questions_db[q_id]
        ee = request.request_body["request"]["nlu"]["entities"]
        number = [e for e in ee if e["type"] == "YANDEX.NUMBER"][0]
        if number["value"] == q.answer:
            text = "Верно!"
        else:
            text = "Не верно!"
        text += f" . Задать еще {q.questiontype.name} вопрос?"
        return self.make_response(text, buttons=[button("Да"), button("Нет")])

    def handle_local_intents(self, request: Request):
        # TODO обработка да и нет
        #     "intents": {
        #     "YANDEX.CONFIRM": {
        #       "slots": {}
        #     }
        #   }
        #  "intents": {
        #     "YANDEX.REJECT": {
        #       "slots": {}
        #     }
        #   }
        return QuestionScene()


class WhoIs(GlobalScene):
    @staticmethod
    def __get_info(id: str):
        with open("guide/persons.csv", mode="r", encoding="utf-8") as infile:
            reader = csv.DictReader(infile, delimiter=";")
            for row in reader:
                if row["id"] == id:
                    return row

    def reply(self, request: Request):

        persona = request.intents[intents.TELL_ABOUT]["slots"]["who"]["value"]
        previous = request.state[STATE_REQUEST_KEY].get("scene", "")
        data = self.__get_info(persona)
        text = data["short"] + "\nПродолжим?"
        card = image_gallery(image_ids=data["gallery"].split(sep="|"))

        return self.make_response(text, card=card, state={"previous": previous})

    def handle_local_intents(self, request: Request):
        if intents.CONFIRM in request.intents:
            return eval(request.state[STATE_REQUEST_KEY]["previous"] + "()")
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
