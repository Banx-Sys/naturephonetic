# Nature Phonetic Translator

A small, cross-platform desktop application for translating text to and from phonetic alphabets. It is a single-file Python 3 program with a Tkinter graphical interface.

The app includes two built-in alphabets:

- **Nature** — a calmer spelling alphabet, from Apple to Zephyr.
- **NATO** — the familiar international radiotelephony spelling alphabet.

## Features

- Translate ordinary text into phonetic words, or reverse the direction to decode phonetic words back into text.
- Switch between the Nature and NATO alphabets at any time.
- Preserve line breaks and punctuation. Spaces between words become `/` in encoded output.
- Mark unrecognised words during decoding as `[?word]` and report how many were found, rather than guessing.
- Copy the result to the clipboard.
- On Windows, speak the translated or entered text aloud, adjust speech rate, and stop speech.
- Run locally without accounts, network services, telemetry, third-party Python packages, or custom alphabet profiles.

## Requirements

- Python 3.10 or later.
- Tkinter, which is included with many Python installations. Some Linux distributions package it separately (often as `python3-tk`).
- A graphical desktop session.

The GUI and translation functions are designed to work on Windows, macOS, and Linux. Text-to-speech uses Windows PowerShell and `System.Speech`, so the **Speak** feature is available only on Windows. On other platforms the application still runs normally, but speaking reports that Windows speech is unavailable.

## Run

Save `nature_phonetic.py` and start it with Python:

```bash
python nature_phonetic.py
```

On some systems, the command may be `python3` instead:

```bash
python3 nature_phonetic.py
```

No installation step or additional Python packages are required.

## Use

1. Enter text in the upper box.
2. Choose **Nature** or **NATO** from the alphabet selector.
3. Read the generated result in the lower box, then choose **Copy result** to copy it.
4. Click the direction button to switch to decoding. The current result moves into the input box so it can be decoded; click the button again to return to encoding.
5. On Windows, use **Speak**, the speed control, and **Stop** to control speech output.

In encoded text, `/` represents a space between words. Line breaks are retained. Decoding is case-insensitive for alphabet words. Words that are not in the selected alphabet are shown in square brackets with a question mark, for example `[?Unknown]`.

## Privacy

Translation is performed on the local computer. The program does not connect to a service or collect telemetry. Windows speech is run locally through PowerShell and `System.Speech`.

## License

No license is specified in this project. Add a license file before redistributing the code if you want to grant others explicit reuse rights.
