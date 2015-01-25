"""Defines shared constants."""
import pyaudio

# Network Constants
PORT = 3000
READY_MESSAGE = 'ready'
ACK_MESSAGE = 'ack'

# Audio Constants
SAMPLE_WIDTH = 2  # bytes per channel
NUM_CHANNELS = 2  # number of channels
FRAME_RATE = 44100  # frame rate in Hz
INPUT_FORMAT = pyaudio.paInt16  # Format for microphone (2-bytes)
INPUT_FRAMES_PER_BUFFER = 32
OUTPUT_FRAMES_PER_BUFFER = 32
