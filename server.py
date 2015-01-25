"""Server that receives and plays audio."""
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


def main():
  def get_data(in_data, frame_count, time_info, status):
    """Callback for pyaudio.Stream.

    Pulls in more data from the connection.
    """
    bytes_needed = phone.SAMPLE_WIDTH * phone.NUM_CHANNELS * frame_count

    # Read a big chunk now
    new_data = connection.recv(2 * bytes_needed)
    print >> sys.stderr, 'Initial read: data = %d, new = %d bytes' % (
       len(data[0]), len(new_data))
    data[0] += new_data
    
    # If that wasn't enough, wait until we've read bytes_needed
    while len(data[0]) < bytes_needed:
      print >> sys.stderr, 'Still need more data...'
      new_data = connection.recv(bytes_needed - len(data[0]))
      data[0] += new_data

    """
    if len(data[0]) - bytes_needed >= phone.MAX_BYTES_BEHIND:
      # We've fallen too far behind--catch up now.
      print >>sys.stderr, 'catching up'
      ret = data[0][len(data[0]) - phone.DESIRED_BYTES_BEHIND - bytes_needed:
                 len(data[0]) - phone.DESIRED_BYTES_BEHIND]
      data[0] = data[0][len(data[0]) - phone.DESIRED_BYTES_BEHIND:]
    else:
    """
    # We're okay, just return from the beginning of data
    # print >>sys.stderr, 'coasting'
    start = time.clock()
    ret = data[0][:bytes_needed]
    data[0] = data[0][bytes_needed:]
    print 'accumulated in buffer %d bytes' % len(data[0])
    end = time.clock()
    print >> sys.stderr, 'get_data took %g seconds' % (end - start)

    return (ret, pyaudio.paContinue)

  # Initialize socket
  sock = InitSocket()
  data = ['']  # Silly hack to let the inner function modify data

  # Make a connection
  connection, client_address = sock.accept()
  print >> sys.stderr, 'Accepted a connection.'

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
      time.sleep(0.1)
    print >> sys.stderr, 'Stream stopped'
  finally:
    connection.close()

  stream.stop_stream()
  stream.close()
  p.terminate()


if __name__ == '__main__':
  main()
