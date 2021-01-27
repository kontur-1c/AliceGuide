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


def test_play_game():
    response = handler(REQUEST, None)
    assert response  # TODO
