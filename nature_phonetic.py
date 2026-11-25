"""Nature Phonetic Translator v2.0 — single-file Windows desktop tool.

Python 3 + tkinter; Windows PowerShell/System.Speech for offline text-to-speech.
No external packages, network services, telemetry, or custom profiles.

Conceptual references (not dependencies or endorsements):
  microsoft::windows  — familiar native desktop interactions
  microsoft::sapi     — Windows speech synthesis
  banx::naturephonetic — a calmer spelling alphabet
"""

from __future__ import annotations

import base64
import re
import subprocess
import sys
import tkinter as tk
from tkinter import ttk


NATURE = (
    "Apple", "Blossom", "Cedar", "Daisy", "Evergreen", "Forest", "Garden",
    "Honey", "Iris", "Jasmine", "Kiwi", "Lavender", "Meadow", "Nectar",
    "Ocean", "Pine", "Quartz", "River", "Sunrise", "Tulip", "Umbrella",
    "Violet", "Willow", "Xylem", "Yucca", "Zephyr",
)
NATO = (
    "Alfa", "Bravo", "Charlie", "Delta", "Echo", "Foxtrot", "Golf",
    "Hotel", "India", "Juliett", "Kilo", "Lima", "Mike", "November",
    "Oscar", "Papa", "Quebec", "Romeo", "Sierra", "Tango", "Uniform",
    "Victor", "Whiskey", "X-ray", "Yankee", "Zulu",
)
PROFILES = {"Nature": NATURE, "NATO": NATO}
TOKEN_RE = re.compile(r"[A-Za-z]+(?:-[A-Za-z]+)*|/|[^\w\s]|\d+|\w+", re.UNICODE)


def encode(text: str, alphabet: tuple[str, ...]) -> str:
    """Spell A–Z; use '/' between words; preserve line breaks and punctuation."""
    lines = []
    for line in text.split("\n"):
        out = []
        for character in line:
            upper = character.upper()
            if len(upper) == 1 and "A" <= upper <= "Z":
                out.append(alphabet[ord(upper) - 65])
            elif character in " \t":
                if out and out[-1] != "/":
                    out.append("/")
            else:
                out.append(character)
        lines.append(" ".join(out))
    return "\n".join(lines)


def decode(text: str, alphabet: tuple[str, ...]) -> tuple[str, list[str]]:
    """Decode known alphabet words, mark unknowns rather than guessing."""
    lookup = {word.casefold(): chr(65 + i) for i, word in enumerate(alphabet)}
    lines = []
    unknown = []
    for line in text.split("\n"):
        chunks = []
        for match in TOKEN_RE.finditer(line):
            token = match.group(0)
            if token == "/":
                chunks.append(" ")
            elif token.casefold() in lookup:
                chunks.append(lookup[token.casefold()])
            elif token.isalpha() or ("-" in token and token[0].isalpha()):
                chunks.append("[?" + token + "]")
                unknown.append(token)
            else:
                chunks.append(token)
        lines.append("".join(chunks))
    return "\n".join(lines), unknown


BG = "#F2F6F4"
WHITE = "#FFFFFF"
INK = "#19382F"
MUTED = "#637970"
GREEN = "#156E55"
GREEN_HOVER = "#0E5B46"
BORDER = "#D5E3DC"
SOFT = "#E8F2ED"
ERROR = "#AD5B38"


class NaturePhoneticApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Nature Phonetic Translator  ·  v2")
        self.geometry("850x690")
        self.minsize(650, 560)
        self.configure(bg=BG)
        self.profile = tk.StringVar(value="Nature")
        self.reverse = False
        self.rate = tk.IntVar(value=0)
        self.status = tk.StringVar(value="Ready to translate")
        self._speech_process: subprocess.Popen | None = None
        self._build()
        self._refresh()
        self.protocol("WM_DELETE_WINDOW", self._close)

    def _label(self, parent, text, **options):
        return tk.Label(parent, text=text, bg=options.pop("bg", BG),
                        fg=options.pop("fg", INK), font=options.pop("font", ("Segoe UI", 10)),
                        **options)

    def _button(self, parent, text, action, *, primary=False, width=None):
        base = GREEN if primary else WHITE
        hover = GREEN_HOVER if primary else SOFT
        foreground = WHITE if primary else GREEN
        button = tk.Button(
            parent, text=text, command=action, bg=base, fg=foreground,
            activebackground=hover, activeforeground=foreground,
            relief="flat", bd=0, cursor="hand2", padx=17, pady=9,
            font=("Segoe UI", 10, "bold"), highlightthickness=1,
            highlightbackground=GREEN if primary else BORDER,
        )
        if width:
            button.configure(width=width)
        button.bind("<Enter>", lambda e: button.configure(bg=hover))
        button.bind("<Leave>", lambda e: button.configure(bg=base))
        return button

    def _build(self) -> None:
        outer = tk.Frame(self, bg=BG, padx=28, pady=23)
        outer.pack(fill="both", expand=True)

        top = tk.Frame(outer, bg=BG)
        top.pack(fill="x")
        self._label(top, "NATURE  /  PHONETIC", fg=GREEN,
                    font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self._label(top, "A clearer way to spell things out.",
                    font=("Segoe UI", 21, "bold")).pack(anchor="w", pady=(7, 1))
        self._label(top, "Quietly useful for calls, names, hostnames and support tickets.",
                    fg=MUTED).pack(anchor="w")

        toolbar = tk.Frame(outer, bg=BG)
        toolbar.pack(fill="x", pady=(22, 14))
        self._label(toolbar, "ALPHABET", fg=MUTED,
                    font=("Segoe UI", 9, "bold")).pack(side="left", padx=(0, 11))
        style = ttk.Style(self)
        if "clam" in style.theme_names():
            style.theme_use("clam")
        style.configure("Nature.TCombobox", padding=7, fieldbackground=WHITE,
                        background=WHITE, foreground=INK, bordercolor=BORDER,
                        arrowcolor=GREEN)
        self.profile_box = ttk.Combobox(toolbar, state="readonly", width=13,
                                        textvariable=self.profile, values=("Nature", "NATO"),
                                        style="Nature.TCombobox")
        self.profile_box.pack(side="left")
        self.profile_box.bind("<<ComboboxSelected>>", lambda e: self._refresh())
        self._label(toolbar, "Two built-in alphabets · fully offline", fg=MUTED,
                    font=("Segoe UI", 9)).pack(side="right")

        self.input_heading = self._label(outer, "PLAIN TEXT", fg=MUTED,
                                         font=("Segoe UI", 9, "bold"))
        self.input_heading.pack(anchor="w", pady=(0, 6))
        self.input_text = tk.Text(outer, wrap="word", height=6, undo=True,
                                  bg=WHITE, fg=INK, insertbackground=GREEN,
                                  selectbackground="#CDE9DC", relief="flat", bd=0,
                                  highlightthickness=1, highlightbackground=BORDER,
                                  highlightcolor=GREEN, padx=15, pady=12,
                                  font=("Segoe UI", 12))
        self.input_text.pack(fill="both", expand=True)
        self.input_text.bind("<<Modified>>", self._input_modified)

        middle = tk.Frame(outer, bg=BG)
        middle.pack(fill="x", pady=11)
        self._label(middle, "Click the arrow to reverse translation",
                    fg=MUTED, font=("Segoe UI", 9)).pack(side="left")
        self.direction_button = self._button(middle, "↓  TEXT TO PHONETIC",
                                              self._toggle_direction)
        self.direction_button.pack(side="right")

        self.output_heading = self._label(outer, "PHONETIC TRANSLATION", fg=MUTED,
                                          font=("Segoe UI", 9, "bold"))
        self.output_heading.pack(anchor="w", pady=(0, 6))
        self.output_text = tk.Text(outer, wrap="word", height=6, bg="#F8FBF9",
                                   fg=INK, relief="flat", bd=0, state="disabled",
                                   highlightthickness=1, highlightbackground=BORDER,
                                   padx=15, pady=12, font=("Segoe UI", 12))
        self.output_text.pack(fill="both", expand=True)

        controls = tk.Frame(outer, bg=BG)
        controls.pack(fill="x", pady=(15, 12))
        self.speak_button = self._button(controls, "▶  Speak", self._speak, primary=True)
        self.speak_button.pack(side="left")
        self._button(controls, "■  Stop", self._stop_speaking).pack(side="left", padx=(7, 0))
        self._label(controls, "Speed", fg=MUTED).pack(side="left", padx=(22, 5))
        tk.Scale(controls, from_=-5, to=5, orient="horizontal", variable=self.rate,
                 bg=BG, fg=INK, activebackground=GREEN, highlightthickness=0,
                 showvalue=True, length=140, resolution=1, troughcolor=SOFT,
                 font=("Segoe UI", 9)).pack(side="left")
        self._button(controls, "Copy result", self._copy_output).pack(side="right")

        foot = tk.Frame(outer, bg=BG)
        foot.pack(fill="x")
        self._label(foot, "v2.0  ·  Windows speech  ·  No account required",
                    fg=MUTED, font=("Segoe UI", 9)).pack(side="right")
        self._label(foot, "", fg=MUTED, font=("Segoe UI", 9),
                    textvariable=self.status).pack(side="left")
        self.input_text.focus_set()

    def _input_modified(self, _event=None) -> None:
        if self.input_text.edit_modified():
            self.input_text.edit_modified(False)
            self._refresh()

    def _get_input(self) -> str:
        return self.input_text.get("1.0", "end-1c")

    def _get_output(self) -> str:
        return self.output_text.get("1.0", "end-1c")

    def _refresh(self) -> None:
        alphabet = PROFILES[self.profile.get()]
        raw = self._get_input()
        if self.reverse:
            result, unknown = decode(raw, alphabet)
            self.status.set(f"{len(unknown)} unrecognised word(s) — marked [?word]" if unknown
                            else "Phonetic → text · ready" )
        else:
            result = encode(raw, alphabet)
            self.status.set("Text → phonetic · ready")
        self.output_text.configure(state="normal")
        self.output_text.delete("1.0", "end")
        self.output_text.insert("1.0", result)
        self.output_text.configure(state="disabled")

    def _toggle_direction(self) -> None:
        # Move the generated result into the input field for a natural round trip.
        next_input = self._get_output()
        self.reverse = not self.reverse
        self.direction_button.configure(
            text="↑  PHONETIC TO TEXT" if self.reverse else "↓  TEXT TO PHONETIC")
        self.input_heading.configure(text="PHONETIC WORDS" if self.reverse else "PLAIN TEXT")
        self.output_heading.configure(text="DECODED TEXT" if self.reverse
                                      else "PHONETIC TRANSLATION")
        self.input_text.delete("1.0", "end")
        self.input_text.insert("1.0", next_input)
        self._refresh()

    def _copy_output(self) -> None:
        result = self._get_output()
        if not result:
            self.status.set("Nothing to copy")
            return
        self.clipboard_clear()
        self.clipboard_append(result)
        self.update_idletasks()
        self.status.set("Result copied to clipboard")

    def _stop_speaking(self) -> None:
        process = self._speech_process
        self._speech_process = None
        if process is not None and process.poll() is None:
            try:
                process.terminate()
            except OSError:
                pass
        self.status.set("Speech stopped")

    def _speak(self) -> None:
        # In reverse mode, read the phonetic input; otherwise read the generated words.
        words = self._get_input() if self.reverse else self._get_output()
        if not words.strip():
            self.status.set("Enter something to speak first")
            return
        if sys.platform != "win32":
            self.status.set("Speech requires Windows PowerShell and System.Speech")
            return
        self._stop_speaking()
        # Encode speech text separately from PowerShell code to avoid script injection.
        encoded_text = base64.b64encode(words.encode("utf-8")).decode("ascii")
        script = (
            "Add-Type -AssemblyName System.Speech; "
            "$s=New-Object System.Speech.Synthesis.SpeechSynthesizer; "
            f"$s.Rate={self.rate.get()}; "
            f"$t=[Text.Encoding]::UTF8.GetString([Convert]::FromBase64String('{encoded_text}')); "
            "$s.Speak($t); $s.Dispose()"
        )
        encoded_script = base64.b64encode(script.encode("utf-16le")).decode("ascii")
        creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        try:
            self._speech_process = subprocess.Popen(
                ["powershell.exe", "-NoProfile", "-NonInteractive", "-EncodedCommand", encoded_script],
                stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL, creationflags=creationflags)
            self.status.set("Speaking · use Stop to interrupt")
        except OSError as exc:
            self.status.set(f"Speech unavailable: {exc}")

    def _close(self) -> None:
        self._stop_speaking()
        self.destroy()


if __name__ == "__main__":
    NaturePhoneticApp().mainloop()
