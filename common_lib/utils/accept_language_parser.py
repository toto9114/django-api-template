def accept_language_parser(
    accept_language: str, reserved_language: tuple = ("en", "ko")
) -> str:
    languages = accept_language.split(",")
    locale_q_pairs = []

    for language in languages:
        if language.split(";")[0] == language:
            locale_q_pairs.append((language.strip(), "1"))
        else:
            locale = language.split(";")[0].strip()
            q = language.split(";")[1].split("=")[1]
            locale_q_pairs.append((locale, q))

        for locale_q_pair in locale_q_pairs:
            if locale_q_pair[0] in reserved_language:
                return locale_q_pair[0]
