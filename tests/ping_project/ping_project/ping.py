from commands import getoutput
PING_CMD = """LANG=C ping %s -c %s | grep 'packet loss' | awk ' { print $ 6} ' | sed 's/\%%//g'""" 
HOSTS = ['ya.ru', 'github.com']

class Host(object):
    __slots__ = ['hostname']
    
    def __init__(self, hostname, ):
        self.hostname = hostname
    
    def __str__(self):
        return self.hostname
    
    def __eq__(self, value):
        return isinstance(value, Host) and self.hostname == value.hostname
    
    def __repr__(self):
        return u'<Host %s>' % self.hostname
    
    def ping(self, count=4):
        res = getoutput(PING_CMD % (self.hostname, count))
        return 100 - int(res)  # 100% - pckages lost %
    
    @classmethod
    def get_list(cls):
        return [Host(h) for h in HOSTS]
    
    
