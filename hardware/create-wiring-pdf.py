#!/usr/bin/env python3
"""Create the printable GIGBOX wiring plan without external PDF packages."""

from pathlib import Path

OUTPUT = Path(__file__).with_name("GIGBOX_GPIO_WIRING_PLAN.pdf")

PAGES = [
    [
        "GIGBOX GPIO WIRING PLAN",
        "Raspberry Pi 5 | BCM numbering | active-low inputs",
        "",
        "SAFETY",
        "- Connect the other side of every control to GND.",
        "- Use internal pull-ups; never apply 5 V to GPIO.",
        "- GPIO 18, 19, 20, 21 are reserved for I2S audio.",
        "- Power off the Pi before wiring and verify with a meter.",
        "",
        "MAIN ENCODER",
        "Signal             BCM     Physical pin",
        "Channel A           5           29",
        "Channel B           6           31",
        "Push switch        13           33",
        "Common             GND      any ground pin",
        "",
        "FIVE-WAY NAVIGATION",
        "Signal             BCM     Physical pin",
        "UP                 17           11",
        "DOWN               27           13",
        "LEFT               22           15",
        "RIGHT              23           16",
        "CLICK              24           18",
        "Common             GND      any ground pin",
        "",
        "GROUND PINS",
        "Physical pins 6, 9, 14, 20, 25, 30, 34, or 39.",
        "All inputs use internal pull-ups and press when connected to ground.",
    ],
    [
        "GIGBOX BUTTON MAP",
        "Button       Function                         BCM     Physical pin",
        "1            Transpose up (+1 semitone)       16          36",
        "2            Transpose down (-1 semitone)      7          26",
        "3            Octave up (+12 semitones)         8          24",
        "4            Octave down (-12 semitones)       9          21",
        "5            Sustain on/off, MIDI CC 64       25          22",
        "6            Play/pause                       26          37",
        "7            Main menu                        12          32",
        "8            Mixer                             4           7",
        "9            ZS3                              10          19",
        "10           ALT                              11          23",
        "",
        "AUDIO RESERVATION - DO NOT USE FOR CONTROLS",
        "I2S clock         BCM 18    Physical pin 12",
        "I2S frame sync    BCM 19    Physical pin 35",
        "I2S data in       BCM 20    Physical pin 38",
        "I2S data out      BCM 21    Physical pin 40",
        "",
        "BRING-UP CHECKLIST",
        "[ ] Pi powered off during wiring",
        "[ ] All control commons connected to GND",
        "[ ] No control wire connected to GPIO 18-21",
        "[ ] Encoder A/B are not swapped",
        "[ ] Every input reads released before pressing",
        "[ ] Test one control at a time with Zynthian control test",
        "",
        "See GIGBOX_GPIO_WIRING_PLAN.md for the complete reference.",
    ],
]


def escape(text):
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def make_page(lines, page_number):
    commands = ["BT", "/F1 10 Tf", "50 750 Td"]
    for line in lines:
        commands.append(f"({escape(line)}) Tj")
        commands.append("0 -16 Td")
    commands.extend([f"(Page {page_number} of {len(PAGES)}) Tj", "ET", "q", "Q"])
    return "BT " + " ".join(commands[1:])


def build_pdf():
    objects = []
    objects.append("<< /Type /Catalog /Pages 2 0 R >>")
    page_refs = " ".join(f"{3 + i * 2} 0 R" for i in range(len(PAGES)))
    objects.append(f"<< /Type /Pages /Kids [{page_refs}] /Count {len(PAGES)} >>")
    for i, lines in enumerate(PAGES):
        content = make_page(lines, i + 1).encode("latin-1")
        objects.append(
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            f"/Resources << /Font << /F1 {3 + len(PAGES) * 2} 0 R >> >> "
            f"/Contents {4 + i * 2} 0 R >>"
        )
        objects.append((f"<< /Length {len(content)} >>\nstream\n").encode("latin-1") + content + b"\nendstream")
    objects.append("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")

    output = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for number, obj in enumerate(objects, 1):
        offsets.append(len(output))
        output.extend(f"{number} 0 obj\n".encode("latin-1"))
        output.extend(obj if isinstance(obj, bytes) else obj.encode("latin-1"))
        output.extend(b"\nendobj\n")
    xref = len(output)
    output.extend(f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode("latin-1"))
    for offset in offsets[1:]:
        output.extend(f"{offset:010d} 00000 n \n".encode("latin-1"))
    output.extend(
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
        f"startxref\n{xref}\n%%EOF\n".encode("latin-1")
    )
    OUTPUT.write_bytes(output)


if __name__ == "__main__":
    build_pdf()
    print(OUTPUT)
