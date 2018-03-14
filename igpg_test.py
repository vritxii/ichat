from igpg import IGPG, KeyInfo

my_uuid = 'ZhongTao (Test) <alice@inter.net>'
recv_uuid = 'Alice <alice@inter.net>'
recv_keyid = '0CE00795'
ig = IGPG(uuid=my_uuid, passphrase='sustech2017')
text_data = b'Hello ICHAT'
sign_data = ig.sign(text_data)
#print(sign_data)
#print(ig.verify(sign_data))
#print(ig.recv(recv_key))
#print(ig.list_keys())
#print(ig.submit('0EF7C70BD2B612F7'))

encry_data = ig.encrypt(text_data, recv_keyid, sign=True)
print('加密并签名')
print(encry_data)
encry_data_1 = ig.encrypt(text_data, recv_keyid)
print('加密不签名')
print(encry_data_1)
print('*****')
encry_data = {'type': 'c', 'content':b'-----BEGIN PGP MESSAGE-----\n\nhQEMA0rqaUEhaXRbAQf+Ko2hmoKklYdupAO/LOrTJ32wJl+6B94cvyVco4W0dSU+\nr5Ae28bNioyVO7KHY6Ibp6cudrGmCpxag0jlLZbBboBUBHKJ0KrCMAETM/dB0JKZ\nXOIQLj8bx9RsGym+u01lDL+nZUf9A9G9kdbwYLdv3nHlEGVPMsLr1JMkigjfeJaV\n7qXc6hLZil35EryX5cwENanC3wSQVXXbBCsFlr44NxNTV0/Zu3sRXyM929BaT5a7\n5ow2YTB7mrexyIGrFxsHNSK789UdG6gmRGfTTie7pjO3iFvm1+Ls1wWt57wGGSig\n+ZgOrABMFqkekI36U0+COMLP5RGtpfiXGDhVqVHgV9LBDQF6dTBOJX5cqvvIWhsj\n+qtuIkG8bAvl2QZ3MEpvcLKmwmlzsid6aQkdglrYRZGtbR9/LE4S4geM8NmT3+0j\ndnvJDBqAt+25TZeZV26xSCfRvLAbHk+YzVAaoNbfxac2UjotvrOCG4+3OlFFNYdl\nwZ+DYn7LmYOFBtzEDWRVVrl8mKLQ+U7LrHSvWOH+kz9u+OaErHCr/CvaIzuewgx+\nYCFxnmZGSVOrvx7qu7GFQDt/Ir7oDCA+JL/1iBzIBeBr3EU2MztFaNJ1r7u6b8+B\nzoaVUPp2fjq7YT1HoHHkKclJ/fljkb3Vhme8zcOVnkjpVWMe/kMSstw60CCdd9bU\nV/aaysraupL+gJaEbQ8dqsdCrLMfL4QkVxm5O8KKrO+0fG7EQXIVbxOx/H1+OXl8\n0c6hiueDKUhvvJhJybeGgO4aaRxoMsWLLIh0MBX8AMp4ocHFehTA34URO45RXGzF\nxv5SYReyJ3k2Uo8mwzw5KjmlsqISItXkbmobHyWdVETsbvB8XjRRObdR3p9626jl\n6x8w8ve+JkUnHntCbO1O7dD8Gd1sspTEeNS/lUC4kCq8xUHMgkjFxWV8n9S4AnOT\nU+bH4VQqz0ZZPiMl2GnD\n=RDeA\n-----END PGP MESSAGE-----\n'}
recover = ig.decrypt(encry_data['content'], sign=True)
recover_1 = ig.decrypt(encry_data_1)

print('验证并解密')
print(recover)
print('解密')
print(recover_1)

'''
ak = ig.search('Alice <alice@inter.net>')
print(ak)
print(ak[0]['keyid'])
print(ig.delete(ak[0]['keyid'], True))
'''
'''
me =  KeyInfo('ZhongTao','alice@inter.net','Test','sustech2017')
key = ig.gen_key(me)
print(key.fingerprint)

try:
    text_data = 'Hello ICHAT'
    print(text_data)
    sign_text=ig.sign(text_data)
    print(sign_text)
    print(ig.verify(sign_text))
except Exception as e:
    print(e)
    pass

finally:
    ig.delete(key.fingerprint, True)

'''