GEOLOCATION_ALLOWED = "Geolocation.Allowed"
GEOLOCATION_REJECTED = "Geolocation.Rejected"


def big_image(image_id, title=None, description=None):
    big_image = {"type": "BigImage", "image_id": image_id}
    if title:
        big_image["title"] = title
    if description:
        big_image["description"] = description

    return big_image


def image_gallery(image_ids):
    if image_ids and image_ids[0] != "":

        items = [{"image_id": image_id} for image_id in image_ids]
        return {
            "type": "ImageGallery",
            "items": items,
        }
    else:
        return {}


def button(title, payload=None, url=None, hide=False):
    button = {
        "title": title,
        "hide": hide,
    }
    if payload is not None:
        button["payload"] = payload
    if url is not None:
        button["url"] = url
    return button


def has_location(event):
    return event["session"].get("location") is not None
