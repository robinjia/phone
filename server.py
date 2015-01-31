"""Server that receives and plays audio."""
import multiprocessing
import os
import pyaudio
import socket
import sys
import time

import phone

# Deals with pulse audio issues on some machines
os.environ['PULSE_LATENCY_MSEC'] = '1'

def InitSocket():
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  server_address = ('0.0.0.0', phone.PORT)
  sock.bind(server_address)
  sock.listen(1)
  print >> sys.stderr, 'Lisetning on %s, port %d' % server_address
  return sock


def ReadBuffers(connection, queue):
  while True:
    data = ''
    bytes_needed = phone.OUTPUT_BYTES_PER_BUFFER
    while bytes_needed > 0:
      new_data = connection.recv(bytes_needed)
      data += new_data
      bytes_needed -= len(new_data)
    queue.put(data)


def main():
  def get_data(in_data, frame_count, time_info, status):
    return (buffer_queue.get(), pyaudio.paContinue)

  # Initialize socket
  sock = InitSocket()

  # Make a connection
  connection, client_address = sock.accept()
  print >> sys.stderr, 'Accepted a connection.'

  # Start child process to listen to connection
  buffer_queue = multiprocessing.Queue()
  child_process = multiprocessing.Process(
      target=ReadBuffers, args=(connection, buffer_queue))
  child_process.start()
  print >> sys.stderr, 'Listening to connection.'

  # Initialize audio stream
  p = pyaudio.PyAudio()
  stream = p.open(format=p.get_format_from_width(phone.SAMPLE_WIDTH),
                  channels=phone.NUM_CHANNELS, rate=phone.FRAME_RATE,
                  output=True, frames_per_buffer=phone.OUTPUT_FRAMES_PER_BUFFER,
                  stream_callback=get_data)

  try:
    print >> sys.stderr, 'Starting stream.'
    stream.start_stream()
    print >> sys.stderr, 'Ready to begin receiving audio.'
    connection.sendall(phone.READY_MESSAGE)
    # Wait for stream to finish
    while stream.is_active():
      print >> sys.stderr, 'buffer_queue.qsize() == %d' % buffer_queue.qsize()
      time.sleep(0.1)
    print >> sys.stderr, 'Stream stopped'
  finally:
    print >> sys.stderr, 'Terminating child process'
    child_process.terminate()
    print >> sys.stderr, 'Closing connection'
    connection.close()
    print >> sys.stderr, 'Closing socket'
    sock.close()
    print >> sys.stderr, 'Closing audio stream'
    stream.close()
    print >> sys.stderr, 'Terminating pyaudio'
    p.terminate()


if __name__ == '__main__':
  main()
