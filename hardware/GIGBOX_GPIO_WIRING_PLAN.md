# GIGBOX GPIO Wiring Plan

**Target:** Raspberry Pi 5, BCM numbering, active-low inputs

## Safety

- Connect the other side of every button, navigation switch, and encoder push switch to GND.
- Use the Raspberry Pi internal pull-ups; do not apply 5 V to GPIO.
- GPIO 18, 19, 20, and 21 are reserved for I2S audio. Do not connect controls to them.
- Power off the Pi before wiring. Verify every wire with a continuity meter before power-up.

## Main Encoder

| Encoder signal | BCM GPIO | Physical pin |
|---|---:|---:|
| Channel A | 5 | 29 |
| Channel B | 6 | 31 |
| Push switch | 13 | 33 |
| Common | GND | 6, 9, 14, 20, 25, 30, 34, or 39 |

Clockwise is increase/next. Counter-clockwise is decrease/previous. Push is SELECT; long press is BACK.

## Five-Way Navigation

| Navigation signal | BCM GPIO | Physical pin |
|---|---:|---:|
| UP | 17 | 11 |
| DOWN | 27 | 13 |
| LEFT | 22 | 15 |
| RIGHT | 23 | 16 |
| CLICK | 24 | 18 |
| Common | GND | Any listed ground pin |

## Ten Buttons

| Button | Function | BCM GPIO | Physical pin |
|---:|---|---:|---:|
| 1 | Transpose up, +1 semitone | 16 | 36 |
| 2 | Transpose down, -1 semitone | 7 | 26 |
| 3 | Octave up, +12 semitones | 8 | 24 |
| 4 | Octave down, -12 semitones | 9 | 21 |
| 5 | Sustain on/off, MIDI CC 64 | 25 | 22 |
| 6 | Play/pause | 26 | 37 |
| 7 | Main menu | 12 | 32 |
| 8 | Mixer | 4 | 7 |
| 9 | ZS3 | 10 | 19 |
| 10 | ALT | 11 | 23 |
| Common | Ground return | GND | Any listed ground pin |

## Ground Pins

Use physical pins **6, 9, 14, 20, 25, 30, 34, or 39**. All inputs use internal pull-ups and are pressed when connected to ground.

## Audio Reservation

| Audio signal | BCM GPIO | Physical pin |
|---|---:|---:|
| I2S clock | 18 | 12 |
| I2S frame sync | 19 | 35 |
| I2S data in | 20 | 38 |
| I2S data out | 21 | 40 |

These four pins must remain dedicated to the PCM DAC.

## Bring-Up Checklist

- [ ] Pi powered off during wiring
- [ ] All control commons connected to GND
- [ ] No control wire connected to GPIO 18-21
- [ ] Encoder A/B are not swapped
- [ ] Every input reads released before pressing any button
- [ ] Test one control at a time with Zynthian control test
