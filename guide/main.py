from alice import AliceResponse
import logging

import sys

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


def handler(event: dict, context=None):

    answer = AliceResponse(event)

    answer.text('Hello')

    return answer.body
