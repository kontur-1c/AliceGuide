from guide.main import handler

false = False
true = True
INITIAL_REQUEST = {
    "meta": {
        "locale": "ru-RU",
        "timezone": "UTC",
        "client_id": "ru.yandex.searchplugin/7.16 (none none; android 4.4.2)",
        "interfaces": {"screen": {}, "payments": {}, "account_linking": {}},
    },
    "session": {
        "message_id": 0,
        "session_id": "13fc52f0-34b2-4e22-9c3d-e46f8dd851d4",
        "skill_id": "03f46589-d3c4-43b1-b8b6-c8118b9ae151",
        "new": true,
    },
    "request": {
        "command": "",
        "original_utterance": "",
        "nlu": {"tokens": [], "entities": [], "intents": {}},
        "markup": {"dangerous_context": false},
        "type": "SimpleUtterance",
    },
    "state": {"session": {}, "user": {}, "application": {}},
    "version": "1.0",
}


def test_welcome():
    response = handler(INITIAL_REQUEST, None)

    # 1. В качестве сцены должны установить начальную
    assert response["session_state"]["scene"] == "Welcome"

    # 2. Среди сценариев должны быть викторина и экскурсия
    button_titles = "\n".join(
        b["title"] for b in response["response"]["buttons"]
    ).lower()
    assert "экскурс" in button_titles
    assert "викторин" in button_titles

    # 3. Навык должен рассказывать о своих возможностях
    assert "я могу" in response["response"]["text"].lower()
