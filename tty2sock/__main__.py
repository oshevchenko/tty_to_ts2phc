from .tty2sock import *

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    host = 'localhost'
    tty_dev = '/dev/ttyUSB1'
    if len(sys.argv) == 2:
        tty_dev = str(sys.argv[1])
    elif len(sys.argv) == 3:
        tty_dev = str(sys.argv[1])
        host = str(sys.argv[2])

    server = PhcServer(host, 4161, tty_dev)

    while True:
        time.sleep(5)
        logging.info('NMEA data {}'.format(server.get_nmea_data()))


    # server.process()
