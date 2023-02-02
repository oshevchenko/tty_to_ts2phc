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
    test1_obj = ThreadSafePhcServerDict(nmea_tags=['GGA', 'RMC', 'XXX'])
    print(test1_obj)
    sss = {'GGA': {'sss': 'dddddd'}}
    test1_obj.update_gnss_data(sss)
    print(test1_obj)
    test1_obj.set_param("xyz",10)
    test1_obj.set_param("xya","11")
    test1_obj.set_param("xyd","12")
    test1_obj.set_param("xyv","13")

    xyz = test1_obj.get_param("xyddz")
    print(type(xyz), xyz)
    print(type(json.dumps(None)))
    xya = test1_obj.get_param("xya")

    print(test1_obj, type(xyz), type(xya))
    test1_obj.set_param("xyz","20")
    xyz1 = test1_obj.get_param("xyz")

    print(test1_obj, xyz, type(xyz1))
    # print(test2_obj.param["xyz"])

