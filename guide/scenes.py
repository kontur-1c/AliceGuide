import csv
import enum
import inspect
import random
import sys
from typing import Union

import guide.texts as texts
from guide import coord, intents, state
from guide.alice import Request
from guide.responce_helpers import GEOLOCATION_ALLOWED, big_image, button, image_gallery
from guide.scenes_util import Scene
from guide.morph import normal_form


class GlobalScene(Scene):
    def reply(self, request: Request):
        pass

    def handle_global_intents(self, request):
        if intents.TELL_ABOUT in request.intents:
            return WhoIs()
        if intents.DEBUG in request.intents:
            return Debug()

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
            location = request["session"]["location"]
            lat = location["lat"]
            lon = location["lon"]
            text = f"Ваши координаты: широта {lat}, долгота {lon}"
            # 58.52113680728278, 31.27517020919651 (координаты памятника)
            km = coord.haversine(
                58.52113680728278, 31.27517020919651, float(lat), float(lon)
            )
            if km > 0.03:
                text += "\nБыло бы здорово находится у памятника"
            else:
                text += "\nСупер, вы рядом с памятником"

            return self.make_response(
                request=request,
                text=text,
                state={state.LOCATION: {"latitude": lat, "longitude": lon}},
            )
        else:
            text = "К сожалению, мне не удалось получить ваши координаты."
            return self.make_response(
                request=request, text=text, directives={"request_geolocation": {}}
            )

    def handle_local_intents(self, request: Request):
        pass


class Welcome(GlobalScene):
    def __init__(self, title=""):
        self.title = title

    def reply(self, request: Request):
        text = self.title + "\n" + texts.welcome()
        # directives = {"request_geolocation": {}}
        return self.make_response(
            request,
            text,
            buttons=[
                button("Сыграть в викторину"),
                button("Расскажи экскурсию"),
            ],
        )

    def handle_local_intents(self, request: Request):
        if intents.START_TOUR in request.intents:
            if state.TOUR_ID in request.state_user:  # есть сохраненное состояние
                return ReturnToTour()
            else:
                return StartNewTour()
        elif intents.START_GAME in request.intents:
            return StartGame()


class Debug(Welcome):
    def reply(self, request: Request):
        text = "Все данные были сброшены" + "\n" + texts.welcome()
        return self.make_response(
            request,
            text,
            buttons=[
                button("Сыграть в викторину"),
                button("Расскажи экскурсию"),
            ],
            user_state=dict((el, None) for el in state.USER_STATE),
        )


# region Quiz


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


def questions_db():
    result = []
    with open("guide/questions.csv", mode="r", encoding="utf-8") as in_file:
        for row in csv.DictReader(in_file, delimiter=","):
            result.append(row)
    return result


def get_questions(question_type: Union[QuestionType, str]):
    if isinstance(question_type, QuestionType):
        type_name = question_type.name
    elif isinstance(question_type, str):
        type_name = question_type
    else:
        raise ValueError("Unknown question_type")
    return [r for r in questions_db() if r["type"] == type_name]


class QuestionScene(GlobalScene):
    def reply(self, request: Request):
        if intents.GAME_QUESTION in request.intents:
            question_type = QuestionType.from_request(request, intents.GAME_QUESTION)
        elif state.QUESTION_TYPE in request.state_session:
            question_type = QuestionType.from_state(request)
        else:
            question_type = QuestionType.simple
        questions = get_questions(question_type)
        asked = request.state_session.get(state.ASKED_QUESTIONS, {})
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
            buttons = (
                [button(v) for v in question["suggest"].split(";")]
                if question["suggest"]
                else []
            )
            asked.update({question_id: None})
            return self.make_response(
                request,
                f"{start_text} {question_text}",
                state={
                    "question_id": question_id,
                    state.ASKED_QUESTIONS: asked,
                },
                buttons=buttons,
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
            return StartNewTour()
        elif intents.START_GAME in request.intents:
            return StartGame()
        else:
            return AnswerScene()


class AnswerScene(GlobalScene):
    @staticmethod
    def get_question(id: int):
        return [r for r in questions_db() if r["id"] == id][0]

    def reply(self, request: Request):
        question_id = request.state_session[state.QUESTION_ID]
        question = self.get_question(question_id)
        answer_type = question["answer_type"]
        if answer_type == "int":
            correct_answer = int(question["answer"])
            nlu_entities = request.request_body["request"]["nlu"]["entities"]
            nlu_numbers = [
                e["value"] for e in nlu_entities if e["type"] == "YANDEX.NUMBER"
            ]
            answered_correctly = correct_answer in nlu_numbers
        elif answer_type == "str":
            tokens = request["request"]["nlu"]["tokens"]
            tokens_norm = [normal_form(t) for t in tokens]
            print(f"morph result: {tokens_norm}")
            answered_correctly = question["answer"].lower() in tokens + tokens_norm
        else:
            raise ValueError(f"Unknown answer type {answer_type}")
        text = question["reply_true"] if answered_correctly else question["reply_false"]
        asked = request.state_session.get(state.ASKED_QUESTIONS, {})
        asked[question_id] = answered_correctly
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
                if set(question_ids) - set(asked)
            ]
            if non_empty_other:
                left_type_names = [t.russian() for t in non_empty_other]
                left_type_names_str = ", ".join(f'"{n}"' for n in left_type_names)
                next_question_prompt = texts.quiz_category_finished(
                    left_type_names_str, len(non_empty_other)
                )
                buttons = [button(n) for n in left_type_names]
                buttons.append(button("Расскажи экскурсию"))
            else:
                num_true = sum(bool(v) for v in asked.values())
                num_total = len(asked)
                next_question_prompt = texts.quiz_finished(num_true, num_total)
                buttons = [button("Расскажи экскурсию"), button("Выйти из навыка")]
        return self.make_response(
            request,
            f"{text} {next_question_prompt}",
            buttons=buttons,
            state={
                state.QUESTION_TYPE: question["type"],
                state.HAVE_MORE_QUESTIONS: have_more_questions,
                state.ASKED_QUESTIONS: asked,
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
            return StartNewTour()
        elif intents.GAME_QUESTION in request.intents:
            return QuestionScene()
        elif intents.REJECT in request.intents:
            return Welcome(texts.reject_new_question())
        elif intents.START_TOUR in request.intents:
            return StartNewTour()
        elif intents.EXIT in request.intents:
            return Goodbye()


# endregion

# region Tour


class StartNewTour(GlobalScene):
    def reply(self, request: Request):
        return self.make_response(
            request,
            texts.start_tour(),
            buttons=YES_NO,
            card=big_image(
                "213044/13a480623796d3b988fd", description=texts.start_tour()
            ),
        )

    def handle_local_intents(self, request: Request):
        if intents.CONFIRM in request.intents:
            return TourStep()
        elif intents.REJECT in request.intents:
            return Welcome(texts.reject_start_tour())
        elif intents.REPEAT in request.intents:
            return StartNewTour()


class ReturnToTour(GlobalScene):
    def reply(self, request: Request):
        id = request.state_user[state.TOUR_ID]
        level = request.state_user[state.TOUR_LEVEL]

        data = _get_tour_data(id, level)

        return self.make_response(
            request,
            texts.continue_tour(data["return_text"]),
            buttons=[button("Напомни"), button("Дальше"), button("Сначала")],
        )

    def handle_local_intents(self, request: Request):
        if intents.RETURN_TOUR in request.intents:
            slots = request.slots(intents.RETURN_TOUR)
            if intents.SLOT_CONTINUE in slots:
                next_id = request.state_user.get(state.TOUR_ID, 0)
                next_level = request.state_user.get(state.TOUR_LEVEL, 0) + 1
                if _get_tour_data(next_id, next_level) is not None:
                    return TourStepLevel()
                else:
                    next_id = request.state_user.get(state.TOUR_ID, 0) + 1
                    next_level = 0
                    if _get_tour_data(next_id, next_level) is not None:
                        return TourStep()
                    else:
                        return TourEnd()
            elif intents.SLOT_REMIND in slots:
                return TourRepeat()
            elif intents.SLOT_NEW in slots:
                return StartNewTour()


class TourStepCommon(GlobalScene):
    def __init__(self):
        self.step_id = 0
        self.step_level = 0
        self.tour_id = 0
        self.tour_level = 0

    def reply(self, request):
        self.tour_id = request.state_user.get(state.TOUR_ID, 0) + self.step_id
        if self.step_level == -1:
            self.tour_level = 0
        else:
            self.tour_level = (
                request.state_user.get(state.TOUR_LEVEL, 0) + self.step_level
            )

        data = _get_tour_data(self.tour_id, self.tour_level)
        text = data["text"]
        tts = data["audio"]
        card = image_gallery(image_ids=data["gallery"].split(sep="|"))
        return self.make_response(
            request,
            text,
            tts=tts,
            buttons=YES_NO,
            card=card,
            user_state={state.TOUR_ID: self.tour_id, state.TOUR_LEVEL: self.tour_level},
        )

    def handle_local_intents(self, request: Request):
        if intents.REPEAT in request.intents:
            return TourRepeat()
        elif intents.BREAK_TOUR in request.intents:
            return Welcome(texts.pause_tour())
        else:
            continue_tour = intents.REJECT in request.intents
            continue_level = (
                intents.CONFIRM in request.intents
                or intents.CONTINUE_TOUR in request.intents
            )
            if continue_level:
                # Есть ли что-то по тому же пути?
                next_id = request.state_user.get(state.TOUR_ID, 0)
                next_level = request.state_user.get(state.TOUR_LEVEL, 0) + 1
                if _get_tour_data(next_id, next_level) is not None:
                    return TourStepLevel()
                else:
                    continue_tour = True
            if continue_tour:
                next_id = request.state_user.get(state.TOUR_ID, 0) + 1
                next_level = 0
                if _get_tour_data(next_id, next_level) is not None:
                    return TourStep()
                else:
                    return TourEnd()


# Это передвижение по фигурам
class TourStep(TourStepCommon):
    def __init__(self):
        super().__init__()
        self.step_id = 1
        self.step_level = -1


# Это дополнительная информация
class TourStepLevel(TourStepCommon):
    def __init__(self):
        super().__init__()
        self.step_id = 0
        self.step_level = 1


class TourRepeat(TourStepCommon):
    def __init__(self):
        super().__init__()
        self.step_id = 0
        self.step_level = 0


class TourEnd(GlobalScene):
    def __init__(self, repeat=False):
        self.repeat = repeat

    def reply(self, request):

        return self.make_response(
            request,
            texts.the_end_of_tour(),
            buttons=YES_NO,
            user_state={state.TOUR_ID: None, state.TOUR_LEVEL: None},
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
            data = [r for r in reader if r["id"] == id]
            if data:
                return data[0]

    def reply(self, request: Request):
        persona = request.intents[intents.TELL_ABOUT]["slots"]["who"]["value"]
        if state.PREVIOUS_SCENE in request.state_session:
            previous = request.state_session[state.PREVIOUS_SCENE]
        else:
            previous = request.state_session.get("scene", "")
        data = self.get_info(persona)
        if data is None:
            text = texts.i_dont_know()
            card = []
        else:
            text = data["short"]
            card = image_gallery(image_ids=data["gallery"].split(sep="|"))
        text += "\nВернемся к тому, где остановились?"

        return self.make_response(
            request,
            text,
            buttons=YES_NO,
            card=card,
            state={state.PREVIOUS_SCENE: previous},
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


def _get_tour_data(id: int, level: int):
    with open("guide/tour.csv", mode="r", encoding="utf-8") as in_file:
        reader = csv.DictReader(in_file, delimiter=",")
        data = [r for r in reader if r["id"] == str(id) and r["level"] == str(level)]
        if data:
            return data[0]


SCENES = {scene.id(): scene for scene in _list_scenes()}

DEFAULT_SCENE = Welcome

YES_NO = [button("Да"), button("Нет")]
