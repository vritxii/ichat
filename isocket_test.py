import isocket
import time

block_info = {'index':101, 'hash':'daggsfdsjkf1286778df8s7t', 'block_hash':'agsdysgdv1765325467gbhg'}
header={'protocol':'ICHAT/1.2', 'op':'Get', 'src':'vritxii@gmail.com', 'method':'Email', 'des':'2582783208@qq.com', 'status':-1, 'sign':1, 'seqnum':10010, 'extra':block_info}
'''
payload = 'Hello'
packet = isocket.Packet()
packet_data = packet.Pack(header, payload)
print(packet_data.decode('utf_8'))
print('*****')
rh, rp = packet.Unpack(packet_data)
print(rh)
print(rp)

print('******')
packet_data = packet.Pack(rh, payload)
print(packet_data.decode('utf_8'))
'''
username = '781442859@qq.com'
password = 'fzomvdkhsgifbdai'

server_mail = '2582783208@qq.com'
server_password = 'kraithshfyqbecad'
send = False
print(header.keys())
iss = isocket.ISocket(server_mail, email_pass=server_password, only='N', server=True, subject='ICHAT')
iss.bind(('127.0.0.1', 9010))
iss.start()

if send:
    iss.send(header)
else:
    index = 0
    header, payload = iss.recv()
    print(index)
    print(header)
    print(len(payload))
    index += 1

    print('Get: ', index)

'''
iss = isocket.ISocket(uuid='nkdzt@foxmail.com', server=True)
iss.bind(('127.0.0.1', 9010))
iss.start()
index = 0
for packet in iss.recv(10):
    print(packet)
    index += 1
print('Get: ', index)
'''
'''
iss.connect(('127.0.0.1',9900))
header = {'op':'msg/text', 'src':'me@', 'des':'1@c', 'seqnum':10080, 'status':-1}
for i in range(5):
    time.sleep(0.5)
    iss.send(header)
time.sleep(100)
'''

def server_test():
    block_info = {'index':101, 'hash':'daggsfdsjkf1286778df8s7t', 'block_hash':'agsdysgdv1765325467gbhg'}
    header={'protocol':'ICHAT/1.2', 'op':'Get', 'src':'vritxii@gmail.com', 'method':'Email', 'des':'2582783208@qq.com', 'status':-1, 'sign':1, 'seqnum':10010, 'extra':block_info}

    pack = isocket.Packet()
    packet = pack.Pack(header)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('127.0.0.1', 9010))
    s.send(b'sustc@163.com')
    s.send(packet)
    time.sleep(10)