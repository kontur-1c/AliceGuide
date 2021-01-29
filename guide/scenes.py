import csv
import enum
import inspect
import random
import sys

from guide import intents
from guide.alice import Request
from guide.responce_helpers import button, image_gallery
from guide.scenes_util import Scene
from guide.state import STATE_REQUEST_KEY


class QuestionType(enum.Enum):
    unknown = 1
    simple = 2
    hard = 3
    attention = 4

    @classmethod
    def from_request(cls, request: Request, intent_name: str):
        slot = request.intents[intent_name]["slots"]["question_type"]["value"]
        if slot == "simple":
            return cls.simple
        elif slot == "hard":
            return cls.hard
        elif slot == "attention":
            return cls.attention
        else:
            return cls.unknown

    @classmethod
    def from_state(cls, request: Request, intent_name: str):
        slot = request.state["session"]["question_type"]
        if slot == "simple":
            return cls.simple
        elif slot == "hard":
            return cls.hard
        elif slot == "attention":
            return cls.attention
        else:
            return cls.unknown

    def russian(self):
        return {
            self.simple: "простой",
            self.hard: "сложный",
            self.attention: "на внимательность",
            self.unknown: "неизвестный",
        }[self]


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
            if question_type != QuestionType.unknown:
                return QuestionScene()


class QuestionScene(GlobalScene):
    @staticmethod
    def get_questions(type: QuestionType):
        with open("guide/questions.csv", mode="r", encoding="utf-8") as in_file:
            reader = csv.DictReader(in_file, delimiter=",")
            return [r for r in reader if r["type"] == type.name]

    def reply(self, request: Request):
        if intents.GAME_QUESTION in request.intents:
            question_type = QuestionType.from_request(request, intents.GAME_QUESTION)
        elif intents.GAME_QUESTION in request.state["session"]:
            question_type = QuestionType.from_state(request, intents.GAME_QUESTION)
        else:
            # TODO продумать логику выборка категории
            # - если пришли из ответа, то нужно использовать тот же тип вопроса
            # - если пришли из начала викторины, то либо распознали интент
            #   либо нужно переспросить / выбрать за пользователя
            question_type = QuestionType.simple
        questions = self.get_questions(question_type)
        if questions:
            # TODO сделать сохранение вопросов, на которые пользователь уже отвечал,
            # выбирать только из неотвеченных
            question = random.choice(questions)
            question_id = question["id"]
            question_text = question["text"]
            self._next_scene = AnswerScene()
            return self.make_response(
                f"Задаю {question_type.russian()} вопрос. {question_text}",
                state={"question_id": question_id},
                buttons=[button(question["answer"])],
            )
        else:
            # TODO сделать более плавный UX
            # например предложить пользователю категорию,
            # в которой еще остались вопросы
            text = (
                "Вы ответили на все вопросы этой категории!"
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
        else:
            return AnswerScene()


class AnswerScene(GlobalScene):
    @staticmethod
    def get_question(id: int):
        with open("guide/questions.csv", mode="r", encoding="utf-8") as in_file:
            reader = csv.DictReader(in_file, delimiter=",")
            return [r for r in reader if r["id"] == id][0]

    def reply(self, request: Request):
        question_id = request.request_body["state"][STATE_REQUEST_KEY]["question_id"]
        question = self.get_question(question_id)
        # TODO поддержать нечисловые типы ответов для вопросов
        # TODO поддержать частично правильный ответ
        correct_answer = int(question["answer"])
        nlu_entities = request.request_body["request"]["nlu"]["entities"]
        nlu_numbers = [e["value"] for e in nlu_entities if e["type"] == "YANDEX.NUMBER"]
        answered_correctly = correct_answer in nlu_numbers
        print(correct_answer, type(correct_answer))
        print(nlu_numbers)
        text = question["reply_true"] if answered_correctly else question["reply_false"]
        return self.make_response(
            f"{text} Задать еще вопрос?",
            buttons=[button("Да"), button("Нет")],
            state={"question_type": question["type"]},
        )

    def handle_local_intents(self, request: Request):
        if intents.CONFIRM in request.intents:
            return QuestionScene()
        elif intents.GAME_QUESTION in request.intents:
            return QuestionScene()
        elif intents.REJECT in request.intents:
            return Welcome()


class WhoIs(GlobalScene):
    @staticmethod
    def __get_info(id: str):
        with open("guide/persons.csv", mode="r", encoding="utf-8") as in_file:
            reader = csv.DictReader(in_file, delimiter=",")
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
