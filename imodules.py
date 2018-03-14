from Crypto.Cipher import AES, PKCS1_OAEP
import json
from socket import *
import string
import random
#Crypto 来自 PyCryptodome、
import rsa
import os

GB = 1024**3
MB = 1024**2
KB = 1024


def LoopDir(d, abspath=False, ext=None):
    all_file = []
    for f in os.listdir(d):   #列出目录下的所以文件及目录
        f = os.path.join(d, f)  #通过os.path.join()函数，把两个路径合成一个时
        if os.path.isfile(f):    #判断是否是文件
            
            if not ext or os.path.splitext(f)[1] == '.' + ext: #判断是否是需要的文件类型
                
                if abspath:
                    
                    all_file.append(os.path.abspath(f)) #打印出绝对路径
                else:
                    all_file.append(f)
        else:  #如果是目录，递归进行
            all_file += LoopDir(f, abspath, ext)
    return all_file


def RandStr(n=8):
    salt = ''.join(random.sample(string.ascii_letters + string.digits, n))
    return salt


def gen_nounce(email, modnum=1000000):
    mer = modnum * 10
    esum = sum([ord(ch) for ch in email])
    nounce = 0
    index = 0
    while ((esum + nounce) % modnum) != 0:
        nounce = int(random.random() * mer)
        index += 1
    return nounce
    pass


def check_nounce(email, nounce, modnum=1000000):
    esum = sum([ord(ch) for ch in email])
    return (esum + nounce) % modnum == 0