import pyaudio
import wave
import time
import aiy.voicehat
from aiy.vision.leds import Leds
from datetime import datetime
from pytz import timezone
import RPi.GPIO as GPIO

#GPIO setting
GPIO.setmode(GPIO.BCM)
_GPIO_BUTTON = 23
GPIO.setup(_GPIO_BUTTON, GPIO.IN)

#LED setting
MAGENTA=(0xFF, 0x00, 0xFF)
BLUE=(0x00, 0x00, 0xFF)

button = aiy.voicehat.get_button()
leds = Leds()

def record_start():
    # File name setting
    now = datetime.now(timezone('Asia/Seoul'))
    y = now.strftime('%Y%m%d_%H%M%S')
    filename = y + '.wav';

    CHUNK = 1024  # 1frame 당 1024개 buffer
    FORMAT = pyaudio.paInt16  # 16-bit int형 signed
    CHANNELS = 1  # mono/stereo
    RATE = 16000  # 16khz
    RECORD_SECONDS = 2
    WAVE_OUTPUT_FILENAME = filename

    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("Start to record the audio.")
    frames = []

    while GPIO.input(_GPIO_BUTTON) == 0:
        leds.update(Leds.rgb_on(MAGENTA))
        data = stream.read(CHUNK)
        frames.append(data)

        # record stream
        if GPIO.input(_GPIO_BUTTON) == 1:
            t_end = time.time() + RECORD_SECONDS
            while time.time() < t_end:
                data = stream.read(CHUNK)
                frames.append(data)
            leds.update(Leds.rgb_off())
            break

    print("Recording is finished.")
    leds.update(Leds.rgb_off())

    # stop stream
    stream.stop_stream()
    stream.close()
    # close PyAudio
    p.terminate()

    wo = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wo.setnchannels(CHANNELS)
    wo.setsampwidth(p.get_sample_size(FORMAT))
    wo.setframerate(RATE)
    wo.writeframes(b''.join(frames))
    wo.close()

    print(WAVE_OUTPUT_FILENAME)

def main():
    leds.update(Leds.rgb_on(BLUE))
    time.sleep(1)

    while True:
        button.wait_for_press()
        record_start()

if __name__ == '__main__':
    main()


