import copy
import json
from types import MethodType


class Chain(object):
    def __getattribute__(self, item):
        fn = object.__getattribute__(self, item)
        if fn and type(fn) == MethodType:

            def chained(*args, **kwargs):
                ans = fn(*args, **kwargs)
                return ans if ans is not None else self

            return chained
        return fn


class AliceResponse(Chain):
    def __init__(self, request):

        self._response_dict = {
            "version": "1.0",
            "session": request["session"],  # для отладки
            "response": {"end_session": False, "buttons": []},
            "session_state": request.get("state", {}).get(
                "session", {}
            ),  # сохраним предыдущее состояние
        }

        self._images = []
        self._header = ""
        self._footer = ""
        self._asItemsList = False
        self._asImageGallery = False

    def __str__(self) -> str:
        return self.dumps()

    def dumps(self):
        return json.dumps(self._response_dict, ensure_ascii=False, indent=2)

    @staticmethod
    def __button(text: str, url: str, payload: str, hide: bool) -> dict:
        button = {"title": text[:64]}
        if url:
            button["url"] = url[:1024]
        if payload:
            button["payload"] = payload
        if hide:
            button["hide"] = hide

        return button

    @staticmethod
    def __buttonImage(text: str, url: str, payload: str) -> dict:
        button = {"text": text[:64]}
        if url:
            button["url"] = url[:1024]
        if payload:
            button["payload"] = payload

        return button

    def __prepare_card(self):
        if not self._images:
            raise Exception("No images for card")
        elif len(self._images) == 1 and not (self._asItemsList or self._asImageGallery):
            result = {"type": "BigImage"}
            result.update(self._images[0])
        elif len(self._images) <= 5 and not self._asImageGallery:
            result = {"type": "ItemsList", "items": copy.deepcopy(self._images)}
        elif len(self._images) <= 7:
            result = {"type": "ImageGallery", "items": copy.deepcopy(self._images)}
        else:
            raise Exception("Too many images")

        if self._header:
            result["header"] = self._header

        if self._footer:
            result["footer"] = self._footer

        return result

    def text(self, text: str):
        """Установить выводимый текст на экран"""
        self._response_dict["response"]["text"] = text[:1024]
        self._response_dict["response"]["tts"] = text[
            :1024
        ]  # по умолчанию произношение совпадает с текстом

    def tts(self, tts: str):
        """Установить произносимую Алисой фразу"""
        self._response_dict["response"][
            "tts"
        ] = tts  # tts может быть длиннее за счет дополнительных звуков

    def setButtons(self, buttons: list):
        """Вывести несколько кнопок

        Параметры:
            buttons -- массив заголовков
        """
        for title in buttons:
            self.button(title)

    def button(self, text: str, url="", payload="", hide=False):
        """Добавить кнопку

        Параметры:
            title -- Текст кнопки, возвращается как выполненная команда request.command
            url -- URL, который должна открывать кнопка
            payload -- Произвольный JSON, который Яндекс.Диалоги должны отправить обработчику,
                        если данная кнопка будет нажата.
            hide -- ризнак того, что кнопку нужно убрать после следующей реплики пользователя.
        """
        button = self.__button(text, url, payload, hide)
        self._response_dict["response"]["buttons"].append(button)

    def image(self, image_id: str, title="", description=""):
        self._images.append(
            {"image_id": image_id, "title": title, "description": description}
        )

    def withButton(self, title: str, url="", payload=""):
        if not self._images:
            raise Exception("No images")
        self._images[-1]["button"] = self.__buttonImage(title, url, payload)

    def header(self, text: str):
        self._header = text

    def footer(self, text: str):
        self._footer = text

    def asItemsList(self):
        assert not self._asImageGallery
        self._asItemsList = True

    def asImageGallery(self):
        assert not self._asItemsList
        self._asImageGallery = True

    def saveState(self, name: str, value):
        """Сохранить переменную в течении сессии
        Получить значения можно в запросе state.session.<name>

        Параметры:
             name -- имя переменной для сохранения
             value -- сохраняемое значение
        """
        self._response_dict["session_state"][name] = value

    def clearState(self):
        """При инициализаци сохранаяется предыдущее состояние
        Это процедура позволяет его очистить"""
        self._response_dict.pop("session_state")

    def end(self):
        """Признак конца разговора"""
        self._response_dict["response"]["end_session"] = True

    @property
    def body(self):
        if self._images:
            self._response_dict["card"] = self.__prepare_card()
        return self._response_dict.copy()


class Request:
    def __init__(self, request_body):
        self.request_body = request_body

    def __getitem__(self, key):
        return self.request_body[key]

    @property
    def intents(self):
        return self.request_body["request"].get("nlu", {}).get("intents", {})

    @property
    def type(self):
        return self.request_body.get("request", {}).get("type")

    @property
    def state(self):
        return self.request_body.get("state", {})
