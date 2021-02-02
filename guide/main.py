import json
import logging
import sys


from guide.alice import Request
from guide.scenes import DEFAULT_SCENE, SCENES
from guide.state import STATE_REQUEST_KEY

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


def handler(event, context):
    request = Request(event)
    print(f"REQUEST {json.dumps(event)}")
    current_scene_id = event.get("state", {}).get(STATE_REQUEST_KEY, {}).get("scene")
    if current_scene_id is None:
        return DEFAULT_SCENE().reply(request)
    current_scene = SCENES.get(current_scene_id, DEFAULT_SCENE)()
    next_scene = current_scene.move(request)
    if next_scene is not None:
        print(f"Moving from scene {current_scene.id()} to {next_scene.id()}")
        return next_scene.reply(request)
    else:
        print(f"Failed to parse user request at scene {current_scene.id()}")
        return current_scene.fallback(request)
