from guide.main import handler

true = True
false = False
REQUEST = {
    "meta": {
        "locale": "ru-RU",
        "timezone": "UTC",
        "client_id": "ru.yandex.searchplugin/7.16 (none none; android 4.4.2)",
        "interfaces": {"screen": {}, "payments": {}, "account_linking": {}},
    },
    "session": {
        "message_id": 1,
        "session_id": "bc84469e-56d3-4828-8f86-219ddeac004f",
        "skill_id": "03f46589-d3c4-43b1-b8b6-c8118b9ae151",
        "new": false,
    },
    "request": {
        "command": "сыграть в викторину",
        "original_utterance": "Сыграть в викторину",
        "nlu": {
            "tokens": ["сыграть", "в", "викторину"],
            "entities": [],
            "intents": {"start_game": {"slots": {}}},
        },
        "markup": {"dangerous_context": false},
        "type": "SimpleUtterance",
    },
    "state": {"session": {"scene": "Welcome"}, "user": {}, "application": {}},
    "version": "1.0",
}


def test_play_game():
    pass
    # response = handler(REQUEST, None)

    # # 1. В качестве сцены должны установить старт викторины
    # assert response["session_state"]["scene"] == "StartGame"

    # # Должены быть кнопки с типами вопросов
    # button_titles = "\n".join(
    #     b["title"] for b in response["response"]["buttons"]
    # ).lower()
    # assert "простой" in button_titles
