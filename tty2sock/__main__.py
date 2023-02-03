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
    data =server.get_nmea_data()
    print(data, type(data))
    while True:
        time.sleep(5)
        logging.info('NMEA data {}'.format(server.get_nmea_data()))
        time.sleep(1)
        server.set_constellation(['GLO', 'GPS', 'BDS'])
        time.sleep(2)
        logging.info('server.get_constellation should be OK {}'.format(server.get_constellation()))
        server.set_constellation(['GLO', 'GPS', 'XXX'])
        time.sleep(2)
        logging.info('server.get_constellation  should be error {}'.format(server.get_constellation()))
        server.set_constellation(['GLO', 'GPS', 'BDS'])
        time.sleep(2)
        logging.info('server.get_constellation should be OK {}'.format(server.get_constellation()))
        server.set_constellation(['GLO', 'GPS', 'XXX'])
        time.sleep(2)
        logging.info('server.get_constellation  should be error {}'.format(server.get_constellation()))

    # server.process()
