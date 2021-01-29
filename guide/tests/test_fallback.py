from guide.main import handler

true = True
false = False

REQUEST = {
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
        "message_id": 4,
        "session_id": "c3c65fb0-16c1-4769-b924-0bb5db5626ea",
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
        "command": "фдылваожфдпрф",
        "original_utterance": "фдылваожфдпрф",
        "nlu": {"tokens": ["фдылваожфдпрф"], "entities": [], "intents": {}},
        "markup": {"dangerous_context": false},
        "type": "SimpleUtterance",
    },
    "state": {
        "session": {"scene": "AnswerScene", "question_type": "simple"},
        "user": {},
        "application": {},
    },
    "version": "1.0",
}


def test_fallback():
    response = handler(REQUEST, None)
    assert response
    assert "Извините" in response["response"]["text"]
    assert "question_type" in response["session_state"]
