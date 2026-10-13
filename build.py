#!/usr/bin/env python3
"""Build the dark-mode block that gets appended to the "Custom CSS" template node."""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent
START = "<!-- cp-dark-mode:start -->"
END = "<!-- cp-dark-mode:end -->"


def block() -> str:
    css = (ROOT / "src/dark-mode.css").read_text()
    js = (ROOT / "src/dark-mode.js").read_text()
    return f'{START}\n<style type="text/css">\n{css}</style>\n<script>\n{js}</script>\n{END}\n'


def strip(fmt: str) -> str:
    """Remove a previously installed block, leaving everything else in the node untouched."""
    if START in fmt and END in fmt:
        head, rest = fmt.split(START, 1)
        _, tail = rest.split(END, 1)
        return head + tail.lstrip("\n")
    return fmt


def install(fmt: str) -> str:
    return strip(fmt).rstrip("\n") + "\n" + block()


if __name__ == "__main__":
    print(block())
