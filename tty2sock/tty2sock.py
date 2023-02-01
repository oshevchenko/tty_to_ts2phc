import serial
import logging
import sys
import socket
import threading
import traceback
import time
import queue
import pynmea2


class PhcServer(object):
    """docstring for PhcServer"""
    TTY_TIMEOUT = float(2.0)
    SOCKET_TIMEOUT = float(10.0)
    MAX_BUFFER_SIZE = 2048
    QUEUE_SIZE = 20
    def __init__(self, host='localhost', port=4161, tty_path=None):
        self._nmea_tags = ['GGA', 'RMC']
        self.data = {}
        for i in self._nmea_tags:
            self.data[i] = {}
        self._host = host
        self._port = port
        self._tty_path = tty_path
        self._tty_running = True
        self._server_running = True
        self._dummy_line = b'$GPGGA,000001.000,,,,,0,00,,,,,,,*79\r\n'
        self._queue = queue.Queue(maxsize=self.QUEUE_SIZE)
        self._condition = threading.Condition()
        self._thr_tty = threading.Thread(target=self._thread_tty)
        self._thr_tty.start()
        self._thr_srv = threading.Thread(target=self._thread_server)
        self._thr_srv.start()


    def start(self):
        if self._tty_running == False:
            self._tty_running = True
            self._thr_tty = threading.Thread(target=self._thread_tty)
            self._thr_tty.start()
        if self._server_running == False:
            self._server_running = True
            self._thr_srv = threading.Thread(target=self._thread_server)
            self._thr_srv.start()


    def stop(self):
        if self._tty_running:
            self._tty_running = False
            self._thr_tty.join()
        if self._server_running:
            self._server_running = False
            self._thr_srv.join()


    def add_tty(self, tty_path):
        try:
            self._tty_running = False
            self._thr_tty.join()
            self._tty_path = tty_path
            self._thr_tty = threading.Thread(target=self._thread_tty)
            self._tty_running = True
            self._thr_tty.start()
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
        while self._server_running:
            try:
                conn, addr = s.accept()
                logging.info('Connected from {}'.format(addr))
                while self._server_running:
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


    def _parse_line(self, line):
        try:
            obj = {}
            gps_data = {}
            nmeaobj = pynmea2.parse(line)
            for i in range(len(nmeaobj.fields)):
                if (i < len(nmeaobj.data)):
                    obj[str(nmeaobj.fields[i][0])] = str(nmeaobj.data[i])
                else:
                    obj[str(nmeaobj.fields[i][0])] = None
            try:
                gps_data[nmeaobj.sentence_type] = obj
            except AttributeError:
                logging.debug("Invalid sentence: {}".format(nmeaobj))

            logging.debug("gps_data: {}".format(gps_data))

            for sm in self._nmea_tags:
                if sm in gps_data:
                    self.data[sm] = gps_data[sm]

        except (pynmea2.nmea.ParseError, pynmea2.nmea.ChecksumError) as e:
            logging.warn("Ignoring line: {}".format(line))


    def _put_line_to_queue(self, line):
        with self._condition:
            try:
                self._queue.put(line, block=False)
            except queue.Full:
                pass
            self._condition.notify()


    def _clear_data(self):
        for i in self._nmea_tags:
            self.data[i] = {}


    def _thread_tty(self):
        """Detect device by sending 'type' command."""
        ser = None
        logging.info('Process started {}'.format(self._tty_path))
        while self._tty_running:
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

                while self._tty_running:
                    line = ser.readline(self.MAX_BUFFER_SIZE)
                    if len(line) == 0:
                        logging.error('Serial timeout!')
                        self._clear_data()
                        continue
                    if len(line) >= self.MAX_BUFFER_SIZE:
                        logging.error('Serial buffer overflow!')
                        self._clear_data()
                        continue
                    if line[0] != '$'.encode()[0]:
                        continue
                    self._parse_line(line.decode('utf-8'))
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
    server = PhcServer('192.168.3.10', 4161, tty_dev)
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
