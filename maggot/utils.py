from maggot.containers import NestedContainer


styles = NestedContainer.from_dict(
    dict(
        reset="\033[0m",
        bold="\033[01m",
        disable="\033[02m",
        underline="\033[04m",
        reverse="\033[07m",
        strikethrough="\033[09m",
        invisible="\033[08m",
        fg=dict(
            black="\033[30m",
            red="\033[31m",
            green="\033[32m",
            orange="\033[33m",
            blue="\033[34m",
            purple="\033[35m",
            cyan="\033[36m",
            lightgrey="\033[37m",
            darkgrey="\033[90m",
            lightred="\033[91m",
            lightgreen="\033[92m",
            yellow="\033[93m",
            lightblue="\033[94m",
            pink="\033[95m",
            lightcyan="\033[96m"
        ),
        bg=dict(
            black="\033[40m",
            red="\033[41m",
            green="\033[42m",
            orange="\033[43m",
            blue="\033[44m",
            purple="\033[45m",
            cyan="\033[46m",
            lightgrey="\033[47m"
        )
    )
)


def formatter(s, style):
    return "{style}{s}\033[00m".format(style=style, s=s)


def bold(s):
    return formatter(s, style=styles.bold)


def red(s):
    return formatter(s, style=styles.fg.red)


def red(s):
    return formatter(s, style=styles.fg.red)


def green(s):
    return formatter(s, style=styles.fg.green)


def blue(s):
    return formatter(s, style=styles.fg.blue)
