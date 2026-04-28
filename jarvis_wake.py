# clap_detector.py

# THRESHOLD: Lower = more sensitive (catches quiet claps, more false positives)
#            Higher = less sensitive (requires louder claps, fewer false triggers)
#            Typical range: 0.1 (sensitive) to 0.5 (loud room)
THRESHOLD = 0.05

import time
import numpy as np
import sounddevice as sd

SAMPLE_RATE = 44100
BLOCK_SIZE = 1024  # Samples per callback (~23ms chunks)

last_clap_time = 0.0
COOLDOWN = 1.0  # Seconds to ignore input after a clap


def audio_callback(indata: np.ndarray, frames: int, time_info, status):
    global last_clap_time

    if status:
        print(f"[WARN] Audio stream status: {status}")

    now = time.monotonic()
    if now - last_clap_time < COOLDOWN:
        return  # Still in cooldown window

    peak = np.max(np.abs(indata))
    if peak > THRESHOLD:
        last_clap_time = now
        print(f"Clap detected! (peak={peak:.3f})")


def main():
    print(f"Listening for claps... (threshold={THRESHOLD})")
    print("Press Ctrl+C to stop.\n")

    try:
        with sd.InputStream(
            samplerate=SAMPLE_RATE,
            blocksize=BLOCK_SIZE,
            channels=1,
            dtype="float32",
            callback=audio_callback,
        ):
            while True:
                time.sleep(0.1)

    except sd.PortAudioError as e:
        print(f"[ERROR] PortAudio failed to open stream: {e}")
        print("Try uncommenting the device listing block at the bottom of this file.")
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()


# ─── FALLBACK: List all audio input devices ───────────────────────────────────
# Uncomment and run if the default mic isn't being picked up.
# Pass the desired device index to sd.InputStream(device=INDEX, ...) above.
#
# import sounddevice as sd
# devices = sd.query_devices()
# for i, d in enumerate(devices):
#     if d["max_input_channels"] > 0:
#         print(f"[{i}] {d['name']} (inputs: {d['max_input_channels']})")
