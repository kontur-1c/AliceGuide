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
        "interfaces": {
          "screen": {},
          "payments": {},
          "account_linking": {},
          "geolocation_sharing": {}
        }
      },
    "session": {
        "message_id": 1,
        "session_id": "eeb9a5f1-18be-459d-8b12-970a7bb6dadf",
        "skill_id": "1f835d35-c640-4c36-b3bc-74ecaa0f71f1",
        "user": {
          "user_id": "5416FF55E3C40C32A49D45D68AA101F9AE1445387749DE5B7BEAAB9CD6557C1D"
        },
        "application": {
          "application_id": "218AE790B7125C9F67E9E3234671E8861D9603BD2627726710B9EF8A1CE9748D"
        },
        "user_id": "218AE790B7125C9F67E9E3234671E8861D9603BD2627726710B9EF8A1CE9748D",
        "new": false
      },
    "request": {
        "command": "кто такой князь владимир",
        "original_utterance": "Кто такой князь Владимир",
        "nlu": {
          "tokens": [
            "кто",
            "такой",
            "князь",
            "владимир"
          ],
          "entities": [
            {
              "type": "YANDEX.FIO",
              "tokens": {
                "start": 3,
                "end": 4
              },
              "value": {
                "first_name": "владимир"
              }
            }
          ],
          "intents": {
            "tell_about": {
              "slots": {
                "who": {
                  "type": "Persons",
                  "tokens": {
                    "start": 2,
                    "end": 4
                  },
                  "value": "KnazVladimir"
                }
              }
            }
          }
        },
        "markup": {
          "dangerous_context": false
        },
        "type": "SimpleUtterance"
      },
    "state": {
        "session": {
          "scene": "StartGame",
          "screen": "start_tour"
        },
        "user": {},
        "application": {}
    },
    "version": "1.0"
}


def test_howis():
    response = handler(REQUEST, None)
    assert response  # TODO
