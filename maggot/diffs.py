import difflib
import json

from maggot.utils import red, green, blue


def color_diff(diff):
    for line in diff:
        if line.startswith('+'):
            yield green(line)
        elif line.startswith('-'):
            yield red(line)
        elif line.startswith('^'):
            yield blue(line)
        else:
            yield line


def colorful_config_diff(a, b):

    a = json.dumps(a.to_dict(), indent=4)
    b = json.dumps(b.to_dict(), indent=4)

    diff = difflib.unified_diff(a.split("\n"), b.split("\n"))
    return "\n".join(color_diff(diff))

