"""Client that sends audio."""
import pyaudio
import socket
import sys
import time
import wave

import phone

def ReadWav(filename):
  wf = wave.open(filename, 'rb')
  print >>sys.stderr, 'sample width = %d' % wf.getsampwidth()
  print >>sys.stderr, 'Num channels = %d' % wf.getnchannels()
  print >>sys.stderr, 'frame rate = %d' % wf.getframerate()
  return wf

def InitMicrophone():
  p = pyaudio.PyAudio()
  stream = p.open(format=phone.INPUT_FORMAT, channels=phone.NUM_CHANNELS,
                  rate=phone.FRAME_RATE, input=True,
                  frames_per_buffer=phone.INPUT_FRAMES_PER_BUFFER)
  return stream


def InitSocket(server_name):
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  server_address = (server_name, phone.PORT)
  sock.connect(server_address)
  print >> sys.stderr, 'Connected to %s:%d' % server_address
  return sock


def WaitForAck(sock, message):
  print >>sys.stderr, 'Waiting for ack from server.'
  data = ''
  while True:
    new_data = sock.recv(8)
    data += new_data
    if data == message:
      break
  print >>sys.stderr, 'Received ack from server.'


def main():
  sock = InitSocket(sys.argv[1])
  from_file = len(sys.argv) > 2
  num_packets_sent = 0
  if from_file:
    wf = ReadWav(sys.argv[2])
  else:
    stream = InitMicrophone()
  try:
    WaitForAck(sock, phone.READY_MESSAGE)
    start_time = time.time()
    prev_time = time.time()
    while True:
      if from_file:
        data = wf.readframes(phone.INPUT_FRAMES_PER_BUFFER)
      else:
        data = stream.read(phone.INPUT_FRAMES_PER_BUFFER)
        print 'Received data of length %d' % len(data)
      if not data:
        break
      # sock.sendall(data)
      cur_time = time.time()
      if num_packets_sent == 0:
        start_time = cur_time
      else:
        print 'Iteration took %g ms (ideal = %g)' % (
            1000 * (cur_time - prev_time),
            1000.0 * phone.INPUT_FRAMES_PER_BUFFER / phone.FRAME_RATE)
        print 'Sent %d packets in %g ms (%g ms per packet)' % (
            num_packets_sent, 1000 * (cur_time - start_time),
            1000 * (cur_time - start_time) / num_packets_sent)
      prev_time = cur_time
      num_packets_sent += 1
  finally:
    sock.close()

  if not from_file:
    stream.stop_stream()
    stream.close()
    p.terminate()


if __name__ == '__main__':
  if len(sys.argv) < 2:
    print >> sys.stderr, (
        'Plays a wave file.\n\nUsage: %s servername [filename.wav]'
        % sys.argv[0])
    sys.exit(-1)
  main()
