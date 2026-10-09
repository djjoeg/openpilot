"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.

How the car setup tools (hondastepper) talk to you: as text in a terminal over SSH, or, when the phone page runs them
(phone.py sets HONDASTEPPER_UI=phone), as one JSON line per message or question, which the page turns into text and
buttons. A question's answer comes back as one line either way.
"""
import json
import os
import sys
from collections.abc import Callable

UI_ENV = "HONDASTEPPER_UI"
PHONE = "phone"

YES_NO = (("y", "Yes"), ("n", "No"))


class Prompter:
  def __init__(self, input_fn: Callable[[str], str] | None = None, print_fn: Callable[[str], None] | None = None,
               ui: str | None = None):
    ui = os.environ.get(UI_ENV, "") if ui is None else ui
    # tests pass their own functions: those always get the terminal text
    self.phone = ui == PHONE and input_fn is None and print_fn is None
    self.input_fn = input_fn if input_fn is not None else input
    self.print_fn = print_fn if print_fn is not None else print

  # ----- phone -----
  @staticmethod
  def _emit(msg: dict) -> None:
    sys.stdout.write(json.dumps(msg) + "\n")
    sys.stdout.flush()

  @staticmethod
  def _read() -> str:
    line = sys.stdin.readline()
    if not line:
      raise EOFError("the phone page stopped answering")
    return line.rstrip("\n")

  # ----- the tools' calls -----
  def say(self, text: str = "") -> None:
    if self.phone:
      self._emit({"t": "say", "text": text})
    else:
      self.print_fn(text)

  def step(self, text: str, button: str = "Done") -> None:
    """Something to do; carries on when it's done (Enter, or the button on the phone)."""
    if self.phone:
      self._emit({"t": "ask", "text": text, "choices": [["", button]], "free_text": False})
      self._read()
    else:
      self.input_fn(f"\n{text}\n  Press Enter when that's done. ")

  def ask(self, text: str, choices: tuple[tuple[str, str], ...] = (), phone_text: str | None = None,
          free_text: bool = False) -> str:
    """A question. choices: (answer, button label) pairs for the phone; free_text: the phone also offers a box to
    type in. phone_text: the question without its typing instructions, for the phone."""
    if self.phone:
      self._emit({"t": "ask", "text": phone_text if phone_text is not None else text,
                  "choices": [list(c) for c in choices], "free_text": free_text or not choices})
      return self._read().strip()
    return self.input_fn(f"\n{text} ").strip()

  def yes_no(self, text: str, phone_text: str | None = None) -> bool | None:
    """True for y, False for n; asks again up to three times, then None."""
    for _ in range(3):
      answer = self.ask(text, YES_NO, phone_text).lower()
      if answer.startswith("y"):
        return True
      if answer.startswith("n"):
        return False
    return None
