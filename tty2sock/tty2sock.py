
class PhcServer(object):
    """docstring for PhcServer"""
    def __init__(self, arg):
        self.arg = arg

    def test(self):
        print("test")

if __name__ == '__main__':
    server = PhcServer(0)
    server.test()
