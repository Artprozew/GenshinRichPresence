from typing import Any


def capitalize_dict(
    obj: dict[str, str],
    *,
    key: bool = True,
    value: bool = True,
    delimiter: str = " ",
    join_sep: str = " ",
) -> dict[str, str]:
    new_dict: dict[str, Any] = {}

    for k, v in obj.items():
        key_words: list[str] = []
        value_words: list[str] = []
        key_str: str = k
        value_str: str = v

        if key:
            for word in k.split(delimiter):
                key_words.append(word.capitalize())

            key_str = join_sep.join(key_words)

        if value:
            for word in v.split(delimiter):
                value_words.append(word.capitalize())

            value_str = join_sep.join(value_str)

        new_dict[key_str] = value_str

    return new_dict


def separate_with(string: str, separator: str) -> str:
    names: list[str] = []
    lowercases: str = ""
    uppercase: str = ""

    # Draft/Workaroundy: Places underscore between uppercased letters
    # e.g. HuTao as Hu_Tao or AmberCN as Amber_CN
    for idx, char in enumerate(string):
        if char.isupper():
            if idx != 0 and string[idx - 1] == uppercase:
                lowercases += char
                continue

            if lowercases:
                names.append(f"{uppercase}{lowercases}")

            lowercases = ""
            uppercase = char
        else:
            lowercases += char

    names.append(f"{uppercase}{lowercases}")
    string = separator.join(names)

    return string
