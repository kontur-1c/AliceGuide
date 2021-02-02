import csv
import enum
import inspect
import random
import sys

from typing import Union

from guide import intents, state, coord
from guide.alice import Request
from guide.responce_helpers import button, image_gallery, big_image, GEOLOCATION_ALLOWED, GEOLOCATION_REJECTED
from guide.scenes_util import Scene
import guide.texts as texts


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
    def from_state(cls, request: Request):
        slot = request.state_session[state.QUESTION_TYPE]
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

    def fallback(self, request: Request):
        save_state = {}
        # Сохраним важные состояние
        for save in state.MUST_BE_SAVE:
            if save in request.state_session:
                save_state.update({save: request.state_session[save]})
        return self.make_response(
            request=request,
            text=texts.i_dont_understand(),
            state=save_state,
        )

class HandleGeolocation(GlobalScene):
    def reply(self, request: Request):
        if request.type == GEOLOCATION_ALLOWED:
            location = request['session']['location']
            lat = location['lat']
            lon = location['lon']
            text = f'Ваши координаты: широта {lat}, долгота {lon}'
            #58.52113680728278, 31.27517020919651 (координаты памятника)
            km = coord.haversine(58.52113680728278, 31.27517020919651, float(lat), float(lon))
            if km > 0.03: 
                text += '\nБыло бы здорово находится у памятника'
            else:
                text += '\nСупер, вы рядом с памятником'
                        
            return self.make_response(
                request=request,
                text=text,
                state={
                    state.LOCATION:{
                        "latitude":lat,
                        "longitude":lon
                    }
                    })
        else:
            text = 'К сожалению, мне не удалось получить ваши координаты.'
            return self.make_response(request=request,text=text, directives={'request_geolocation': {}})        

    def handle_local_intents(self, request: Request):
        pass

class Welcome(GlobalScene):
    def __init__(self, title=""):
        self.title = title

    def reply(self, request: Request):
        text = self.title + "\n" + texts.welcome()
        directives = {'request_geolocation': {}}
        return self.make_response(
            request,
            text,
            buttons=[
                button("Сыграть в викторину"),
                button("Расскажи экскурсию"),
            ],
            directives=directives
        )

    def handle_local_intents(self, request: Request):
        if intents.START_TOUR in request.intents:
            if state.TOUR_ID in request.state_session:  # есть сохраненное состояние
                return ContinueTour()
            else:
                return StartTour()
        elif intents.START_GAME in request.intents:
            return StartGame()
        elif request.type in (
            GEOLOCATION_ALLOWED, 
            GEOLOCATION_REJECTED,
        ):
            return HandleGeolocation()


# region Quiz


class StartGame(GlobalScene):
    def reply(self, request: Request):
        text = texts.start_quiz()
        return self.make_response(
            request,
            text,
            buttons=[
                button("Простой"),
                button("Сложный"),
                button("На внимательность"),
            ],
            state={state.QUESTION_TYPE: "simple"},
        )

    def handle_local_intents(self, request: Request):
        question_type = QuestionType.unknown
        if intents.GAME_QUESTION in request.intents:
            question_type = QuestionType.from_request(request, intents.GAME_QUESTION)
        elif intents.CONFIRM in request.intents:
            question_type = QuestionType.from_state(request)
        elif intents.REJECT in request.intents:
            return Welcome(texts.reject_continue_quiz())
        if question_type != QuestionType.unknown:
            return QuestionScene()


def get_questions(question_type: Union[QuestionType, str]):
    if isinstance(question_type, QuestionType):
        type_name = question_type.name
    elif isinstance(question_type, str):
        type_name = question_type
    else:
        raise ValueError("Не правильный тип question_type")
    with open("guide/questions.csv", mode="r", encoding="utf-8") as in_file:
        reader = csv.DictReader(in_file, delimiter=",")
        return [r for r in reader if r["type"] == type_name]


class QuestionScene(GlobalScene):
    def reply(self, request: Request):
        if intents.GAME_QUESTION in request.intents:
            question_type = QuestionType.from_request(request, intents.GAME_QUESTION)
        elif state.QUESTION_TYPE in request.state_session:
            question_type = QuestionType.from_state(request)
        else:
            question_type = QuestionType.simple
        questions = get_questions(question_type)
        asked = set(request.state_session.get(state.ASKED_QUESTIONS, []))
        not_asked = [q for q in questions if q["id"] not in asked]
        if not_asked:
            question = random.choice(not_asked)
            question_id = question["id"]
            question_text = question["text"]
            start_text = {
                "simple": "Задаю простой вопрос.",
                "hard": "Задаю сложный вопрос.",
                "attention": "Задаю вопрос на внимательность.",
            }[question_type.name]
            return self.make_response(
                request,
                f"{start_text} {question_text}",
                state={
                    "question_id": question_id,
                    state.ASKED_QUESTIONS: list(asked) + [question_id],
                },
                buttons=[button(question["answer"])],
            )
        else:
            return self.make_response(
                request,
                texts.run_out_of_questions(),
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
        question_id = request.state_session[state.QUESTION_ID]
        question = self.get_question(question_id)
        # TODO поддержать нечисловые типы ответов для вопросов
        # TODO поддержать частично правильный ответ
        correct_answer = int(question["answer"])
        nlu_entities = request.request_body["request"]["nlu"]["entities"]
        nlu_numbers = [e["value"] for e in nlu_entities if e["type"] == "YANDEX.NUMBER"]
        answered_correctly = correct_answer in nlu_numbers
        text = question["reply_true"] if answered_correctly else question["reply_false"]
        asked = set(request.state_session.get(state.ASKED_QUESTIONS, []))
        questions = get_questions(question["type"])
        not_asked = [q for q in questions if q["id"] not in asked]
        if len(not_asked) > 0:
            have_more_questions = True
            next_question_prompt = {
                "simple": "Задать еще простой вопрос?",
                "hard": "Задать еще сложный вопрос?",
                "attention": "Задать еще вопрос на внимательность?",
            }[question["type"]]
            buttons = YES_NO
        else:
            have_more_questions = False
            question_type = QuestionType[question["type"]]
            other_categories = [
                (t, [q["id"] for q in get_questions(t)])
                for t in QuestionType
                if t != question_type and t != QuestionType.unknown
            ]
            non_empty_other = [
                question_type
                for question_type, question_ids in other_categories
                if set(question_ids) - asked
            ]
            if non_empty_other:
                left_type_names = [t.russian() for t in non_empty_other]
                left_type_names_str = ", ".join(f'"{n}"' for n in left_type_names)
                if len(non_empty_other) == 1:
                    category_word = "в категории"
                    move_phrase = "А еще у нас есть экскурсия! К чему перейдем?"
                else:
                    category_word = "в категориях"
                    move_phrase = "К какой перейдем?"
                next_question_prompt = (
                    "\n\nПоздравляю! "
                    "Вы ответили на все вопросы этой категории! "
                    f"У нас остались вопросы {category_word} {left_type_names_str}. "
                    f"{move_phrase}"
                )
                buttons = [button(n) for n in left_type_names]
                buttons.append(button("Расскажи экскурсию"))
            else:
                next_question_prompt = (
                    "\n\nПоздравляю! "
                    "Вы ответили на все вопросы викторины! "
                    "Рассказать экскурсию?"
                )
                buttons = [button("Расскажи экскурсию"), button("Выйти из навыка")]
        return self.make_response(
            request,
            f"{text} {next_question_prompt}",
            buttons=buttons,
            state={
                state.QUESTION_TYPE: question["type"],
                state.HAVE_MORE_QUESTIONS: have_more_questions,
            },
        )

    def handle_local_intents(self, request: Request):
        if (
            intents.CONFIRM in request.intents
            or intents.MORE_QUESTIONS in request.intents
        ) and request.state_session[state.HAVE_MORE_QUESTIONS]:
            return QuestionScene()
        elif (
            intents.CONFIRM in request.intents
            and not request.state_session[state.HAVE_MORE_QUESTIONS]
        ):
            return StartTour()
        elif intents.GAME_QUESTION in request.intents:
            return QuestionScene()
        elif intents.REJECT in request.intents:
            return Welcome(texts.reject_new_question())
        elif intents.START_TOUR in request.intents:
            return StartTour()
        elif intents.EXIT in request.intents:
            return Goodbye()


# endregion

# region Tour


class StartTour(GlobalScene):
    def reply(self, request: Request):
        return self.make_response(
            request,
            texts.start_tour(),
            buttons=YES_NO,
            card=big_image("213044/3187944dd73678b67180"),
            state={state.TOUR_ID: 1, state.TOUR_LEVEL: 0}            
        )

    def handle_local_intents(self, request: Request):
        if intents.CONFIRM in request.intents:
            return TourStep()
        elif intents.REJECT in request.intents:
            return Welcome(texts.reject_start_tour())
        elif intents.REPEAT in request.intents:
            return StartTour()


class ContinueTour(GlobalScene):
    def reply(self, request: Request):
        id = request.state_session[state.TOUR_ID] - 1
        # как и в повторе сохранено уже следующее состояние
        level = request.state_session[state.TOUR_LEVEL]

        data = _get_tour_data(id)

        return self.make_response(
            request,
            texts.continue_tour(data["return_text"]),
            buttons=YES_NO,
            state={state.TOUR_ID: id + 1, state.TOUR_LEVEL: level},
        )

    def handle_local_intents(self, request: Request):
        if (
            intents.CONFIRM in request.intents
            or intents.CONTINUE_TOUR in request.intents
        ):
            return TourStep()
        elif intents.REJECT in request.intents:
            return StartTour()


class TourStep(GlobalScene):
    def __init__(self, repeat=False):
        self.repeat = repeat

    def reply(self, request):
        id = request.state_session[state.TOUR_ID]
        if self.repeat:
            id -= 1
        level = request.state_session[state.TOUR_LEVEL]
        data = _get_tour_data(id)
        if data is None:

            return self.make_response(
                request,
                texts.the_end_of_tour(),
                buttons=YES_NO,
                state={state.TOUR_ID: 0, state.TOUR_LEVEL: 0},
            )
        else:
            text = data["text"] + "\nПродолжим?"
            card = image_gallery(image_ids=data["gallery"].split(sep="|"))
            return self.make_response(
                request,
                text,
                buttons=YES_NO,
                card=card,
                state={state.TOUR_ID: id + 1, state.TOUR_LEVEL: 0},
            )

    def handle_local_intents(self, request: Request):
        if (
            intents.CONFIRM in request.intents
            or intents.CONTINUE_TOUR in request.intents
        ):
            id = request.state_session[state.TOUR_ID]
            data = _get_tour_data(id)
            if data is None:
                return TourEnd()
            else:
                return TourStep()
        elif intents.REJECT in request.intents or intents.BREAK in request.intents:
            return Welcome(texts.pause_tour())
        elif intents.REPEAT in request.intents:
            return TourStep(True)


class TourEnd(GlobalScene):
    def __init__(self, repeat=False):
        self.repeat = repeat

    def reply(self, request):

        return self.make_response(
            request,
            texts.the_end_of_tour(),
            buttons=YES_NO,
            state={state.TOUR_ID: 0, state.TOUR_LEVEL: 0},
        )

    def handle_local_intents(self, request: Request):
        if intents.CONFIRM in request.intents:
            return Welcome()
        elif intents.REJECT in request.intents:
            return Goodbye()


class Goodbye(GlobalScene):
    def reply(self, request):

        return self.make_response(request, texts.goodbye(), end_session=True)


# endregion


class WhoIs(GlobalScene):
    @staticmethod
    def get_info(id: str):
        with open("guide/persons.csv", mode="r", encoding="utf-8") as in_file:
            reader = csv.DictReader(in_file, delimiter=",")
            return [r for r in reader if r["id"] == id][0]

    def reply(self, request: Request):
        persona = request.intents[intents.TELL_ABOUT]["slots"]["who"]["value"]
        if state.PREVIOUS_SCENE in request.state_session:
            previous = request.state_session[state.PREVIOUS_SCENE]
        else:
            previous = request.state_session.get("scene", "")
        data = self.get_info(persona)
        text = data["short"] + "\nПродолжим?"
        card = image_gallery(image_ids=data["gallery"].split(sep="|"))

        return self.make_response(
            request, text, card=card, state={state.PREVIOUS_SCENE: previous}
        )

    def handle_local_intents(self, request: Request):
        if intents.CONFIRM in request.intents:
            return eval(request.state_session[state.PREVIOUS_SCENE] + "()")
        elif intents.REJECT in request.intents:
            return Welcome("Тогда вернемся в самое начало.")


def _list_scenes():
    current_module = sys.modules[__name__]
    scenes = []
    for name, obj in inspect.getmembers(current_module):
        if inspect.isclass(obj) and issubclass(obj, Scene):
            scenes.append(obj)
    return scenes


def _get_tour_data(id: int, level=0):
    with open("guide/tour.csv", mode="r", encoding="utf-8") as in_file:
        reader = csv.DictReader(in_file, delimiter=",")
        data = [r for r in reader if r["id"] == str(id)]
        if data:
            return data[0]


SCENES = {scene.id(): scene for scene in _list_scenes()}

DEFAULT_SCENE = Welcome

YES_NO = [button("Да"), button("Нет")]
