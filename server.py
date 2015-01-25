"""Server that receives and plays audio."""
import pyaudio
import socket
import sys
import time

import phone

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
    data = ''
    bytes_needed = phone.SAMPLE_WIDTH * phone.NUM_CHANNELS * frame_count
    while len(data) < bytes_needed:
      new_data = connection.recv(min(4096, bytes_needed))
      data += new_data
    return (data, pyaudio.paContinue)

  # Initialize socket
  sock = InitSocket()

  # Make a connection
  connection, client_address = sock.accept()
  print >> sys.stderr, 'Accepted a connection.'

  # Initialize audio stream
  p = pyaudio.PyAudio()
  stream = p.open(format=p.get_format_from_width(phone.SAMPLE_WIDTH),
                  channels=phone.NUM_CHANNELS,
                  rate=phone.FRAME_RATE,
                  output=True,
                  stream_callback=get_data)

  try:
    print >> sys.stderr, 'Starting stream.'
    stream.start_stream()
    print >> sys.stderr, 'Stream started.'
    # Wait for stream to finish
    while stream.is_active():
      time.sleep(0.1)
  finally:
    connection.close()

  stream.stop_stream()
  stream.close()
  wf.close()
  p.terminate()


if __name__ == '__main__':
  main()
