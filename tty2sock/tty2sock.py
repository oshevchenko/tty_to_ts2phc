import serial
import logging
import sys
import socket
import threading
import traceback
import time
import queue


class PhcServer(object):
    """docstring for PhcServer"""
    TTY_TIMEOUT = float(2.0)
    SOCKET_TIMEOUT = float(10.0)
    MAX_BUFFER_SIZE = 2048
    QUEUE_SIZE = 20
    def __init__(self, host='localhost', port=4161, tty_path=None):
        self._host = host
        self._port = port
        self._tty_path = tty_path
        self._running = True
        self._dummy_line = b'$GPGGA,000001.000,,,,,0,00,,,,,,,*79\r\n'
        self._queue = queue.Queue(maxsize=self.QUEUE_SIZE)
        self._condition = threading.Condition()
        self._thr = threading.Thread(target=self._thread_tty)
        self._thr.start()
        self._thr_sock = threading.Thread(target=self._thread_server)
        self._thr_sock.start()


    def add_tty(self, tty_path):
        try:
            self._running = False
            self._thr.join()
            self._tty_path = tty_path
            self._thr = threading.Thread(target=self._thread_tty)
            self._running = True
            self._thr.start()
        except Exception as e:
            logging.error(e)
            logging.error(traceback.format_exc())
            pass


    def _thread_server(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self._host, self._port))
        s.listen(1)
        s.settimeout(self.SOCKET_TIMEOUT)
        conn = None
        while True:
            try:
                conn, addr = s.accept()
                logging.info('Connected from {}'.format(addr))
                while True:
                    with self._condition:
                        self._condition.wait()
                        while True:
                            try:
                                line = self._queue.get(block=False)
                                conn.sendall(line)
                            except queue.Empty:
                                break
            except (OSError, FileNotFoundError):
                # /dev/ttyUSB0 does not exist.
                logging.warning('ts2phc socket error!')
                pass
            finally:
                if conn:
                    conn.close()
                    conn = None
            time.sleep(1)


    def _put_line_to_queue(self, line):
        with self._condition:
            try:
                self._queue.put(line, block=False)
            except queue.Full:
                pass
            self._condition.notify()


    def _thread_tty(self):
        """Detect device by sending 'type' command."""
        ser = None
        logging.info('Process started {}'.format(self._tty_path))
        while self._running:
            try:
                ser = serial.Serial(
                    port=self._tty_path,\
                    baudrate=115200,\
                    parity=serial.PARITY_NONE,\
                    stopbits=serial.STOPBITS_ONE,\
                    bytesize=serial.EIGHTBITS,\
                    timeout=self.TTY_TIMEOUT)

                ser.flushInput()
                ser.flushOutput()

                while self._running:
                    line = ser.readline(self.MAX_BUFFER_SIZE)
                    if len(line) == 0:
                        logging.error('Serial timeout!')
                        continue
                    if len(line) >= self.MAX_BUFFER_SIZE:
                        logging.error('Serial buffer overflow!')
                        continue
                    if line[0] != '$'.encode()[0]:
                        continue
                    self._put_line_to_queue(line)
            except (OSError, FileNotFoundError):
                # /dev/ttyUSB0 does not exist.
                logging.info('Serial: {} error!'.format(self._tty_path))
                pass
            except serial.SerialException as e:
                logging.error('Serial exception! {}'.format(e))
                pass
            finally:
                self._put_line_to_queue(self._dummy_line)
                if ser:
                    ser.close()
                    ser = None
            time.sleep(1)



if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    tty_dev = '/dev/ttyUSB1'
    if len(sys.argv) == 2:
        tty_dev = str(sys.argv[1])
    server = PhcServer('192.168.3.10', 4161)
    time.sleep(5)
    server.add_tty('/dev/ttyUSB2')
    time.sleep(10)
    server.add_tty('/dev/ttyUSB1')
    time.sleep(10)
    server.add_tty('/dev/ttyUSB2')
    time.sleep(10)
    server.add_tty('/dev/ttyUSB1')
    time.sleep(10)
    server.add_tty('/dev/ttyUSB2')
    time.sleep(10)
    server.add_tty('/dev/ttyUSB1')
    time.sleep(10)

    # server.process()
