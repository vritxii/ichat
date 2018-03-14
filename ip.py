import requests
import time
import threading
import subprocess
import socket
import struct
import sys

class ITimer:
    def __init__(self):
        pass

    def start(self):
        self._t = time.time()

    def end(self):
        return time.time()-self._t

def OuternalIP(url='http://ip-api.com/', timeout=3, onlyip=True, debug=False):
    ip_info = {}
    text = ''
    def GetIP():
        nonlocal ip_info, text
        r = requests.post(url)
        text = r.text
        
    t = threading.Thread(target=GetIP, args=())
    t.setDaemon(True)
    t.start()
    t.join(timeout)
    if debug and text == '':
        text = '\x1b[39m{\n  \x1b[96m"country"     \x1b[39m: \x1b[92m"China"\x1b[39m,\n  \x1b[96m"countryCode" \x1b[39m: \x1b[92m"CN"\x1b[39m,\n  \x1b[96m"region"      \x1b[39m: \x1b[92m"44"\x1b[39m,\n  \x1b[96m"regionName"  \x1b[39m: \x1b[92m"Guangdong"\x1b[39m,\n  \x1b[96m"city"        \x1b[39m: \x1b[92m"Shenzhen"\x1b[39m,\n  \x1b[96m"zip"         \x1b[39m: \x1b[92m""\x1b[39m,\n  \x1b[96m"lat"         \x1b[39m: \x1b[95m22.5333\x1b[39m,\n  \x1b[96m"lon"         \x1b[39m: \x1b[95m114.1333\x1b[39m,\n  \x1b[96m"timezone"    \x1b[39m: \x1b[92m"Asia/Shanghai"\x1b[39m,\n  \x1b[96m"isp"         \x1b[39m: \x1b[92m"China Telecom Guangdong"\x1b[39m,\n  \x1b[96m"org"         \x1b[39m: \x1b[92m"China Telecom"\x1b[39m,\n  \x1b[96m"as"          \x1b[39m: \x1b[92m"AS4134 No.31,Jin-rong Street"\x1b[39m,\n  \x1b[96m"mobile"      \x1b[39m: \x1b[94mfalse\x1b[39m,\n  \x1b[96m"proxy"       \x1b[39m: \x1b[94mfalse\x1b[39m,\n  \x1b[96m"query"       \x1b[39m: \x1b[92m"59.40.188.37"\n\x1b[39m}\n'
    arr1 = text.split('\x1b[39m')[1:-1]
    arr2 = []
    for k in range(len(arr1)):
        try:
            arr2.append(arr1[k].split('\"')[1].strip())
        except Exception as e:
            arr2.append(arr1[k].split('m')[1].strip())
        if k%2 != 0:
            ip_info[arr2[k-1]] = arr2[k]
    if onlyip:
        return ip_info['query']
    return ip_info

def InternalIP():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip

def Traceroute(url='ip-api.com', timeout=0, debug=False):
    it = ITimer()
    it.start()
    p = subprocess.Popen("traceroute "+url,shell=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
    #print(it.end())
    try:
        p.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        #print('Time out')
        pass

    ip = []
    lines = []
    if debug:
        print(it.end())
        it.start()
    while True:
        line = p.stdout.readline()
        if not line:
            break
        try:
            newip = line.split(b'(')[1].split(b')')[0]
            ip.append(newip.decode('utf_8'))
        except Exception as e:
            pass
    if debug:
        print(ip)
        print('Run time: ', it.end())
    if len(ip)>1:
        return ip[1:]
    return ip
    pass

def GetIPInfo():
    ip_info = {}
    ip_info['internal'] = InternalIP()
    ip_info['outernal'] = OuternalIP()
    ip_info['trace'] = Traceroute()
    ip_info['direct'] = (ip_info['internal'] == ip_info['outernal'])
    return ip_info
    pass

def CompareIPS(a:list, b:list):
    if a[0] in b:
        '''
        如果a的第一跳路由在b的路由中，说明b能直接连接a
        '''
        return 0
    if b[0] in a:
        return 1
    return -1
    pass

if __name__ == '__main__':
    '''
    ip_a = [b'192.168.99.1', b'10.22.0.1', b'183.56.68.241', b'59.38.107.205', b'183.56.65.22', b'202.97.94.134', b'202.97.94.90', b'59.43.244.133', b'218.30.48.194', b'173.254.205.146', b'96.44.180.34', b'66.212.29.250']
    ip_b = [b'10.22.0.1', b'183.56.68.241', b'59.38.107.205', b'183.56.65.22', b'202.97.94.134', b'202.97.94.90', b'59.43.244.133', b'218.30.48.194', b'173.254.205.146', b'96.44.180.34', b'66.212.29.250']
    print(CompareIPS(ip_a, ip_b))
    print(GetIPInfo())
    '''
    print(type(InternalIP))
