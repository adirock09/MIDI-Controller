import board
import digitalio
import analogio
import usb_midi
import time

import adafruit_midi
from adafruit_midi.note_on import NoteOn
from adafruit_midi.note_off import NoteOff
from adafruit_midi.control_change import ControlChange


# ---------------- MIDI ----------------

midi = adafruit_midi.MIDI(
    midi_out=usb_midi.ports[1],
    out_channel=0
)


# ---------------- MATRIX PINS ----------------

ROWS = [
    board.GP2,
    board.GP3,
    board.GP4,
    board.GP5
]

COLS = [
    board.GP6,
    board.GP7,
    board.GP8,
    board.GP9,
    board.GP10,
    board.GP11,
    board.GP12,
    board.GP13,
    board.GP14,
    board.GP15
]


row_pins = []
col_pins = []

for r in ROWS:
    pin = digitalio.DigitalInOut(r)
    pin.direction = digitalio.Direction.OUTPUT
    pin.value = True
    row_pins.append(pin)

for c in COLS:
    pin = digitalio.DigitalInOut(c)
    pin.direction = digitalio.Direction.INPUT
    pin.pull = digitalio.Pull.UP
    col_pins.append(pin)


pressed = [[False]*10 for _ in range(4)]


# ---------------- NOTE MAP ----------------

HIGH_NOTES = [
72,74,76,77,79,81,83,84,86,88,
89,91,93,95,96,98,100,101,103,105
]

LOW_NOTES = [
48,50,52,53,55,57,59,60,62,64,
65,67,69,71,72,74,76,77,79,81
]


# ---------------- SLIDERS ----------------

slider1 = analogio.AnalogIn(board.GP26)
slider2 = analogio.AnalogIn(board.GP27)
slider3 = analogio.AnalogIn(board.GP28)

last_slider1 = 0
last_slider2 = 0
last_slider3 = 0


# ---------------- KEY SCAN ----------------

def scan_matrix():

    for r in range(4):

        row_pins[r].value = False

        for c in range(10):

            if not col_pins[c].value:

                if not pressed[r][c]:

                    if r < 2:
                        note = HIGH_NOTES[r*10 + c]
                    else:
                        note = LOW_NOTES[(r-2)*10 + c]

                    midi.send(NoteOn(note,120))
                    pressed[r][c] = True

            else:

                if pressed[r][c]:

                    if r < 2:
                        note = HIGH_NOTES[r*10 + c]
                    else:
                        note = LOW_NOTES[(r-2)*10 + c]

                    midi.send(NoteOff(note,0))
                    pressed[r][c] = False

        row_pins[r].value = True


# ---------------- SLIDERS ----------------

def read_sliders():

    global last_slider1
    global last_slider2
    global last_slider3

    v1 = slider1.value >> 9
    v2 = slider2.value >> 9
    v3 = slider3.value >> 9

    if abs(v1 - last_slider1) > 2:
        midi.send(ControlChange(74, v1))
        last_slider1 = v1

    if abs(v2 - last_slider2) > 2:
        midi.send(ControlChange(91, v2))
        last_slider2 = v2

    if abs(v3 - last_slider3) > 2:
        midi.send(ControlChange(1, v3))
        last_slider3 = v3


# ---------------- MAIN LOOP ----------------

while True:

    scan_matrix()

    read_sliders()

    time.sleep(0.005)