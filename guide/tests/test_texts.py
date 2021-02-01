from pyaspeller import YandexSpeller

import pytest
import guide.texts as texts

speller = YandexSpeller()

cases = {
    "i_dont_understand",
    "start_quiz",
    "reject_continue_quiz",
    "reject_new_question",
    "run_out_of_questions",
    "start_tour",
    "reject_start_tour",
    "pause_tour",
    "the_end_of_tour",
    "goodbye",
}


@pytest.mark.parametrize("function", cases)
def test_typos(function):
    text = getattr(texts, function)
    assert speller.spelled(text()) == text()
