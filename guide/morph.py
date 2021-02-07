import pymorphy2

morph = pymorphy2.MorphAnalyzer()


def normal_form(s: str) -> str:
    return morph.parse(s)[0].normal_form
