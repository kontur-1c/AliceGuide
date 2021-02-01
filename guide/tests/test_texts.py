from pyaspeller import YandexSpeller

import pytest
import guide.texts as texts

speller = YandexSpeller()

cases = {
    "IDnotUnderstand",
    "StartQuiz",
    "RejectContinueQuiz",
    "RejectNewQuestion",
    "RunOutOfQuestions",
    "StartTour",
    "RejectStartTour",
    "PauseTour",
    "TheEndOfTour",
    "Goodbye",
}


@pytest.mark.parametrize("function", cases)
def test_typos(function):
    text = getattr(texts, function)
    assert speller.spelled(text()) == text()
