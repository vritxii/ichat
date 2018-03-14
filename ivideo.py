import socket
import image as Image
import os,sys,pygame
from pygame.locals import *
import numpy as np
import cv2
import threading
import time
import struct
import pickle
import zlib
import pyaudio
import wave

close_video = False
resolution = (860, 480)

class FrameSocket:
    __clisocket = None
    __buf_size = None

    def __init__(self, addr, buf_size=4096):
        self.__clisocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__clisocket.bind(addr)
        self.__buf_size = buf_size
    
    def connect(self, other_addr):
        print(other_addr)
        self.__clisocket.connect(other_addr)
        pass
    
    def sendall(self, frame, fmt='L'):
        data = pickle.dumps(frame)
        zdata = zlib.compress(data, zlib.Z_BEST_COMPRESSION)
        
        self.__clisocket.sendall(struct.pack(fmt, len(zdata)) + zdata)
        print("video send ", len(zdata))

    def recvall(self, buf_size=81920, fmt='L'):
        payload_size = struct.calcsize(fmt)
        while True:
            data = "".encode("utf-8")
            while len(data) < payload_size:
                data += self.__clisocket.recv(buf_size)

            packed_size = data[:payload_size]
            data = data[payload_size:]
            msg_size = struct.unpack("L", packed_size)[0]
            while len(data) < msg_size:
                data += self.__clisocket.recv(81920)
            zframe_data = data[:msg_size]
            data = data[msg_size:]
            frame_data = zlib.decompress(zframe_data)
            frame = pickle.loads(frame_data)
            yield frame
        pass

    def sendframe(self, frame, to_addr):
        index = 0
        buf_size = self.__buf_size - 1
        next_index = buf_size
        data = img2bytes(frame)
        N = len(data)
        while next_index < N:
            self.__clisocket.sendto(b'1' + data[index:next_index],to_addr)
            index = next_index
            next_index += buf_size

        self.__clisocket.sendto(b'0' + data[index:N], to_addr)
        pass

    def recvframe(self, buf=False):
        buf_img = []
        while 1:
            data = self.__clisocket.recv(self.__buf_size)
            buf_img.extend(data[1:])
            if data[0] == 48:
                buf_img = bytes(buf_img)
                #print('get %d' % len(buf_img))
                if buf:
                    yield buf_img
                else:
                    frame = bytes2img(buf_img)
                    res = cv2.resize(frame,resolution, interpolation = cv2.INTER_CUBIC)
                    yield res
                buf_img = []
        pass

    def sendAudioFrame(self, audio_data, to_addr=None, fmt='L'):
        data = struct.pack("L", len(audio_data)) + audio_data
        index = 0
        buf_size = self.__buf_size - 1
        next_index = buf_size
        N = len(data)
        while next_index < N:
            self.__clisocket.sendto(b'1' + data[index:next_index],to_addr)
            index = next_index
            next_index += buf_size
        self.__clisocket.sendto(b'0' + data[index:N], to_addr)
        pass
        pass

    def recvAudioFrame(self, fmt='L'):
        #data = "".encode("utf-8")
        data = []
        payload_size = struct.calcsize(fmt)
        buf_size = self.__buf_size
        buf_audio = []
        while True:
            data = self.__clisocket.recv(self.__buf_size)
            buf_audio.extend(data[1:])
            if data[0] == 48:
                msg_size = struct.unpack(fmt, buf_audio)[0]
                frame_data = buf_audio[:msg_size]
                frames = pickle.loads(frame_data)
                for frame in frames:
                    yield frame
            data = []
        pass

    def recvfrom(self, max_size):
        buf_data = []
        cur_size = 0
        while 1:
            if self.__buf_size > max_size:
                yield self.__clisocket.recvfrom(max_size)
            else:
                '''
                data, address = self.__clisocket.recvfrom(self.__buf_size)
                cur_size += len(data)
                buf_data.extend(date)
                if cur_size == max_size:
                    yield (buf_data, address)
                    cur_size = 0
                    buf_img = []
                '''
                yield self.__clisocket.recvfrom(max_size)
        pass

    def send_signal(self):
        pass

    def recv_signal(self):
        pass

    def close(self):
        self.__clisocket.close()
        pass
        

def img2bytes(img):
    img_bytes = cv2.imencode('.jpg', img)[1].tostring()
    return img_bytes

def bytes2img(img_bytes):
    '''
    enum
    {
    /* 8bit, color or not */
        CV_LOAD_IMAGE_UNCHANGED  =-1,
    /* 8bit, gray */
        CV_LOAD_IMAGE_GRAYSCALE  =0,
    /* ?, color */
        CV_LOAD_IMAGE_COLOR      =1,
    /* any depth, ? */
        CV_LOAD_IMAGE_ANYDEPTH   =2,
    /* ?, any color */
        CV_LOAD_IMAGE_ANYCOLOR   =4
    };
    '''
    nparr = np.fromstring(img_bytes, np.uint8)
    #img = cv2.imdecode(nparr, cv2.CV_LOAD_IMAGE_COLOR)
    img = cv2.imdecode(nparr, 4)
    return img

def read_frame():
    cap = cv2.VideoCapture(0) # 从摄像头中取得视频
    cap.set(3,resolution[0])
    cap.set(4, resolution[1])
    # 获取视频播放界面长宽
    #width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) + 0.5)
    #height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) + 0.5)

    # 定义编码器 创建 VideoWriter 对象
    #fourcc = cv2.VideoWriter_fourcc(*'mp4v') # Be sure to use the lower case
    #out = cv2.VideoWriter('output.mp4', fourcc, 20.0, (width, height))
    # cv2.namedWindow('My_Camera', cv2.WINDOW_NORMAL)
    while(cap.isOpened()):
        #读取帧摄像头
        ret, frame = cap.read()
        if ret == True:
            #输出当前帧
            #out.write(frame)
            #cv2.imshow('My_Camera',frame)
            res = cv2.resize(frame,resolution, interpolation = cv2.INTER_CUBIC)

            yield res
            #键盘按 Q 退出
            if (cv2.waitKey(1) & 0xFF) == ord('q') or close_video:
                break
        else:
            break

    # 释放资源
    #out.release()
    cap.release()
    #cv2.destroyAllWindows()

black = (0,0,0)
white = (255,255,255)

def make_surface(frame):
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = np.rot90(frame)
    frame = pygame.surfarray.make_surface(frame)
    return frame

def struct_frame(frame):
    data = pickle.dumps(frame)
    zdata = zlib.compress(data, zlib.Z_BEST_COMPRESSION)
    return struct.pack("L", len(zdata)) + zdata

def recover_frame(zdata, fmt='L'):
    payload_size = struct.calcsize(fmt)

    

class VoiceCall:
    __myname = ''
    __withwho = ''
    __state = False
    __lock = None

    def __init__(self, me_info, towho_info):
        self.__myname = me_info[0]
        self.__withwho = towho_info[0]
        self.__my_s_addr = me_info[1]
        self.__my_r_addr = (me_info[1][0],me_info[1][1]+1)
        self.__other_r_addr = (towho_info[1][0],towho_info[1][1]+1)
        self.__lock = threading.Lock()

    def video_server(self):
        sf = FrameSocket(self.__my_s_addr)
        sf.connect(self.__other_r_addr)
        for frame in read_frame():
            # print('frame size %d' % len(img_bytes))
            if not self.__state:
                break
            #sf.sendall(frame)
            sf.sendframe(frame, self.__other_r_addr)
        sf.close()

    def video_show(self):
        pygame.init()
        screen = pygame.display.set_mode(resolution)
        pygame.display.set_caption("web cam")
        pygame.display.flip()
        clock = pygame.time.Clock()    #计算帧速

        svrsocket = FrameSocket(self.__my_r_addr)

        ik = 0

        for recv_img in svrsocket.recvframe():
            camshot = make_surface(recv_img)
            '''
            cv2.namedWindow('You', cv2.WINDOW_NORMAL)
            cv2.imshow('You', recv_img)
            if cv2.waitKey(1) & 0xFF == 27:
                cv2.destroyWindow('You')
            '''
            for event in pygame.event.get():
                    if event.type == pygame.QUIT: 
                        self.stop()
                        #sys.exit(0)
                        return

            screen.blit(camshot, (0,0))
            pygame.display.update() 
            print(clock.get_fps())     #在终端打印帧速
            clock.tick()

    def run(self):
        self.__state = True
        server_t = threading.Thread(target=self.video_server, args=())
        #server_t.setDaemon(True)
        server_t.start()
        time.sleep(1)
        show_t = threading.Thread(target=self.video_show, args=())
        #show_t.setDaemon(True)
        show_t.start()

        #server_t.join()
        #show_t.join()

    def stop(self):
        self.__lock.acquire()
        self.__state = False
        self.__lock.release()


CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 0.5
Default_Host = '192.168.99.101'

class AudioCall:
    __myname = ''
    __withwho = ''
    __state = False
    __lock = None

    def __init__(self, me_info, towho_info):
        self.__myname = me_info[0]
        self.__withwho = towho_info[0]
        self.__my_s_addr = me_info[1]
        self.__my_r_addr = (me_info[1][0],me_info[1][1]+1)
        self.__other_r_addr = (towho_info[1][0],towho_info[1][1]+1)
        self.__lock = threading.Lock()
        self.p = pyaudio.PyAudio()
        self.stream = None

    def __del__(self):
        if self.stream is not None:
            try:
                self.stream.stop_stream()
                self.stream.close()
            except:
                pass
        if self.p is not None:  
            try:
                self.p.terminate()
            except:
                pass

    def audio_server(self):
        audio_server_socket = FrameSocket(self.__my_s_addr)
        print ("Start Audio Server...")
        self.stream = self.p.open(format=FORMAT, 
                             channels=CHANNELS,
                             rate=RATE,
                             input=True,
                             frames_per_buffer=CHUNK)

        while self.stream.is_active():
            frames = []
            for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
                data = self.stream.read(CHUNK)
                frames.append(data)
            senddata = pickle.dumps(frames)
            print('send audio block')
            try:
                audio_server_socket.sendAudioFrame(senddata, self.__other_r_addr)
            except Exception as e:
                print('hehhe')

        audio_server_socket.close()

    def audio_play(self):
        audio_recv_socket = FrameSocket(self.__my_r_addr)
        self.stream = self.p.open(format=FORMAT,
                                  channels=CHANNELS,
                                  rate=RATE,
                                  output=True,
                                  frames_per_buffer = CHUNK
                                  )
        for audio_frame in audio_recv_socket.recvAudioFrame():
            self.stream.write(audio_frame, CHUNK)

    def run(self):
        self.__state = True
        server_t = threading.Thread(target=self.audio_server, args=())
        #server_t.setDaemon(True)
        server_t.start()
        time.sleep(1)
        play_t = threading.Thread(target=self.audio_play, args=())
        #show_t.setDaemon(True)
        play_t.start()

    def stop(self):
        self.__lock.acquire()
        self.__state = False
        self.__lock.release()

if __name__ == '__main__':
    me = ('zt', (Default_Host,9988))
    you = ('su', ("127.0.0.1",9900))
    #mv = AudioCall(me, me)
    yv = VoiceCall(you, you)
    #mt = threading.Thread(target=mv.run, args=())
    yt = threading.Thread(target=yv.run, args=())

    #mt.setDaemon(True)
    #yt.setDaemon(True)

    #mt.start()
    yt.start()