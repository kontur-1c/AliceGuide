import random
import math


def i_dont_understand():
    return "Извините, я вас не поняла. Пожалуйста, попробуйте переформулировать вопрос."


def i_dont_know():
    texts = [
        "Кажется про него я пока ничего не знаю. Но прочитаю книжки и узнаю.",
        "Извините, нет пока информации. Но скоро появится.",
        "Ой. А кто? Даже самой стало интересно. Спроси меня попозже, я обо всем узнаю.",
        "Хм. Хороший вопрос. Пойду поищу на него ответ.",
    ]
    return random.choice(texts)


def welcome():
    return (
        "Я могу провести экскурсию по памятнику, "
        "могу рассказать, про каждую фигуру на памятнике, "
        "а можем сыграть в викторину"
    )


# region Texts for Quiz


def start_quiz():
    return (
        "Вопросы бывают простые, сложные и на внимательность.\n"
        "В простых вопросах будут варианты ответа.\n"
        "В сложных подсказок не будет.\n"
        'А чтобы правильно ответить на вопрос "На внимательность" хорошо бы видеть сам памятник '
        "или его фотографии.\n"
        "Начнем с простого вопроса?"
    )


def reject_continue_quiz():
    return "У нас очень интересные вопросы. Попробуйте сыграть потом."


def reject_new_question():
    return "Хорошо, тогда вернемся в начало."


def run_out_of_questions():
    return (
        "Вы ответили на все вопросы этой категории! "
        "Я могу провести экскурсию по памятнику "
        "могу рассказать, про каждую фигуру на памятнике "
        "а можем сыграть в викторину"
    )


def quiz_category_finished(left_type_names_str, num_categories_left):
    if num_categories_left == 1:
        category_word = "в категории"
        move_phrase = "А еще у нас есть экскурсия! К чему перейдем?"
    else:
        category_word = "в категориях"
        move_phrase = "К какой перейдем?"
    return (
        "\n\nПоздравляю! "
        "Вы ответили на все вопросы этой категории! "
        f"У нас остались вопросы {category_word} {left_type_names_str}. "
        f"{move_phrase}"
    )


def phi(x, mean, std_deviation):
    "Cumulative distribution function for the normal distribution"
    return (1 + math.erf((x - mean) / std_deviation / math.sqrt(2))) / 2


def quiz_finished(num_true, num_total):
    true_proportion = num_true / num_total
    if true_proportion == 1:
        more_than = 1
    elif true_proportion == 0:
        more_than = 0
    else:
        more_than = phi(true_proportion, mean=0.25, std_deviation=0.3)
    return (
        "\n\nПоздравляю! "
        "Вы ответили на все вопросы викторины!\n"
        f"Верных ответов {num_true} из {num_total}.\n"
        f"Вы дали больше верных ответов, чем {more_than*100:.0f}% участников!\n"
        "Рассказать экскурсию?"
    )


# endregion


# region Tour


def start_tour():
    return (
        "Я готова начать экскурсию, она занимает примерно 100 минут, за это время мы обойдем памятник по кругу."
        "Узнаем кто и зачем его установил и какое значение памятник приобрел для Великого Новгорода."
        "Если устанете слушать и захотите сделать перерыв - дайте мне знать."
        "Начинаем?"
    )


def reject_start_tour():
    return (
        "Зря отказываетесь. У нас очень интересная экскурсия."
        "Но я еще много чего умею."
    )


def more_tour():
    return "Я могу рассказать об этом больше или повести вас дальше. Продолжим тут?"


def next_step_tour():
    texts = [
        "Переходим к следующей фигуре?",
        "Идемте дальше?",
        "Готовы слушать дальше?",
    ]
    return random.choice(texts)


def continue_tour(return_text: str):
    return (
        f"В прошлый раз мы закончили на {return_text}. "
        f"Скажите Повтори, и я напомню на чем остановились."
        f"Скажите Да и мы пойдем дальше."
        f"Скажите Нет, чтобы начать экскурсию заново."
    )


def pause_tour():
    return "Хорошо. На этом пока закончим. Возвращайтесь в любое время." "А пока..."


def the_end_of_tour():
    return (
        "На этом наша экскурсия закончена. Спасибо, что были с нами. "
        "Обязательно сыграйте в викторину, там есть очень интересные вопросы. "
        "Или можете еще раз послушать экскурсию, если что-то пропустили."
        "Возвращаемся в главное меню?"
    )


# endregion


def goodbye():
    return "До новых встреч. Не забудьте поставить оценку нашему навыку"
