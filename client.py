"""Client that sends audio."""
import pyaudio
import socket
import sys
import wave

import phone

def ReadWav(filename):
  wf = wave.open(sys.argv[1], 'rb')
  print >>sys.stderr, 'sample width = %d' % wf.getsampwidth()
  print >>sys.stderr, 'Num channels = %d' % wf.getnchannels()
  print >>sys.stderr, 'frame rate = %d' % wf.getframerate()
  return wf

def InitSocket():
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  server_address = (phone.SERVER_NAME, phone.PORT)
  sock.connect(server_address)
  print >> sys.stderr, 'Connected to %s:%d' % server_address
  return sock


def main():
  wf = ReadWav(sys.argv[1])
  sock = InitSocket()
  try:
    while True:
      data = wf.readframes(1)
      if not data:
        break
      sock.sendall(data)
  finally:
    sock.close()


if __name__ == '__main__':
  if len(sys.argv) < 2:
    print >> sys.stderr, 'Plays a wave file.\n\nUsage: %s filename.wav' % sys.argv[0]
    sys.exit(-1)
  main()
