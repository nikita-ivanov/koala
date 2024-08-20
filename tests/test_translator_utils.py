from tools import translate


def test_translate():
    input_sentence = "Hallo Welt, wie geht es?"
    translated_setnence = translate(input_sentence)

    assert isinstance(translated_setnence, str)
    assert len(translated_setnence) >= 10  # at least 10 characters
    assert len(translated_setnence.split()) >= 4  # at least 4 words
