from dataclasses import dataclass, field
import typing
import threading
import json


@dataclass
class ThreadSafeDict:
    # param: Dict[str, str] = field(default_factory = lambda: ({"xyz": 0}))
    tsd: typing.Dict[str, str] = field(default_factory = lambda: ({}))
    lock: threading.Lock = field(repr=False, init=False)

    def __post_init__(self):
        self.lock = threading.Lock()


    def set_param(self, name, value):
        with self.lock:
            self.tsd[name] = json.dumps(value)


    def get_param(self, name):
        with self.lock:
            return json.loads(self.tsd.get(name, 'null'))


if __name__ == '__main__':

    sss = {'const': ['GLO', 'GPS', 'BDS'], 'status': 'TODO'}
    test1_obj = ThreadSafeDict()
    test1_obj.set_param('set_const', sss)
    print(test1_obj)
    cmd = test1_obj.get_param('set_const')
    if cmd['status'] == 'TODO':
        satellites = cmd['const']
        set_const_cmd = '$PTWSMODE,CONST,SET'

        for sat in satellites:
            set_const_cmd = set_const_cmd + ',' + sat
        set_const_cmd += '\r\n'
        print(set_const_cmd.encode('utf-8'))
        # sock.write(set_const_cmd.encode('utf-8'))
