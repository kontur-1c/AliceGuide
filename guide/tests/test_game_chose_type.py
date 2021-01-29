from guide.main import handler

true = True
false = False

response = {
    "response": {"text": "Задаю простой вопрос...", "tts": "Задаю простой вопрос..."},
    "version": "1.0",
    "session_state": {"scene": "SimpleQuestion"},
}

REQUEST = {
    "meta": {
        "locale": "ru-RU",
        "timezone": "UTC",
        "client_id": "ru.yandex.searchplugin/7.16 (none none; android 4.4.2)",
        "interfaces": {"screen": {}, "payments": {}, "account_linking": {}},
    },
    "session": {
        "message_id": 2,
        "session_id": "bc84469e-56d3-4828-8f86-219ddeac004f",
        "skill_id": "03f46589-d3c4-43b1-b8b6-c8118b9ae151",
        "new": false,
    },
    "request": {
        "command": "простой",
        "original_utterance": "Простой",
        "nlu": {
            "tokens": ["простой"],
            "entities": [],
            "intents": {
                "game_question": {
                    "slots": {
                        "question_type": {
                            "type": "QuestionType",
                            "tokens": {"start": 0, "end": 1},
                            "value": "simple",
                        }
                    }
                }
            },
        },
        "markup": {"dangerous_context": false},
        "type": "SimpleUtterance",
    },
    "state": {
        "session": {"scene": "StartGame", "screen": "start_tour"},
        "user": {},
        "application": {},
    },
    "version": "1.0",
}

REQUEST_ANSWER = {
    "meta": {
        "locale": "ru-RU",
        "timezone": "UTC",
        "client_id": "ru.yandex.searchplugin/7.16 (none none; android 4.4.2)",
        "interfaces": {
            "screen": {},
            "payments": {},
            "account_linking": {},
            "geolocation_sharing": {},
        },
    },
    "session": {
        "message_id": 15,
        "session_id": "8f977edd-e362-4201-a5ee-738e7a3941c3",
        "skill_id": "1f835d35-c640-4c36-b3bc-74ecaa0f71f1",
        "user": {
            "user_id": "5416FF55E3C40C32A49D45D68AA101F9AE1445387749DE5B7BEAAB9CD6557C1D"
        },
        "application": {
            "application_id": "218AE790B7125C9F67E9E3234671E8861D9603BD2627726710B9EF8A1CE9748D"
        },
        "user_id": "218AE790B7125C9F67E9E3234671E8861D9603BD2627726710B9EF8A1CE9748D",
        "new": false,
    },
    "request": {
        "command": "7",
        "original_utterance": "7",
        "nlu": {
            "tokens": ["7"],
            "entities": [
                {"type": "YANDEX.NUMBER", "tokens": {"start": 0, "end": 1}, "value": 7}
            ],
            "intents": {},
        },
        "markup": {"dangerous_context": false},
        "type": "SimpleUtterance",
    },
    "state": {
        "session": {
            "scene": "QuestionScene",
            "question_id": "3",
            "question_type": "simple",
        },
        "user": {},
        "application": {},
    },
    "version": "1.0",
}


def test_play_game():
    response = handler(REQUEST, None)
    assert response
    assert "Задаю простой вопрос" in response["response"]["text"]


def test_answer_question():
    response = handler(REQUEST_ANSWER, None)
    assert response
    assert (
        response["session_state"]["question_type"] == "simple"
    )  # Сохранили тип вопроса
    assert "Верно" in response["response"]["text"]
