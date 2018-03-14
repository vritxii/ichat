import gnupg

def KeyInfo(name_real, name_email, name_comment, passpharse, expire_date=0, key_type='RSA', key_usage='', key_length=2048, subkey_type='RSA', subkey_length=1024, subey_usage='encrypt,sign,auth'):
    '''
        key_info example:
            key_info = {   'name_real': 'ZhongTao',
                'name_email': 'alice@inter.net',
                'name_comment': 'Test',
                'expire_date': 0,
                'key_type': 'RSA',
                'key_length': 2048,
                'key_usage': '',
                'subkey_type': 'RSA',
                'subkey_length': 1024,
                'subkey_usage': 'encrypt,sign,auth',
                'passphrase': 'sustech2017'}
    '''
    return {    'name_real': name_real,
                'name_email': name_email,
                'name_comment': name_comment,
                'expire_date': expire_date,
                'key_type': key_type,
                'key_length': key_length,
                'key_usage': key_usage,
                'subkey_type': subkey_type,
                'subkey_length': subkey_length,
                'subkey_usage': subey_usage,
                'passphrase': passpharse
            }

class IGPG:
    def __init__(self, uuid, passphrase=None, keyserver = 'pgp.mit.edu', homedir='~/.gnupg'):
        self.__uuid = uuid
        self.__homedir = homedir
        self.__keyserver = keyserver
        self.__gpg = gnupg.GPG(gnupghome=self.__homedir)
        self.__gpg.encoding = 'utf_8'
        self.__fingerprint = self.get_fingerprint(self.__uuid, True)
        self.__passphrase = passphrase
        

    def get_fingerprint(self, uid, priv=False):
        list_keys = self.__gpg.list_keys(priv)
        for key in list_keys:
            if uid in key['uids']:
                return key['fingerprint']
        return None
        pass

    def get_keyid(self, uid):
        pubkeys = self.__gpg.list_keys()
        keyid = None
        keyids = []
        print('UID: ', uid)
        for key in pubkeys:
            if uid in key['uids']:
                keyid = key['keyid']
                break
        if not keyid:
            keyids = self.recv_by_uid(uid)
        if len(keyids) > 0:
            keyid = keyids[0]
        if keyid:
            return keyid[-8:]
        else:
            return None
        pass

    def gen_key(self, key_info):
        key_input = self.__gpg.gen_key_input(**key_info)
        key = self.__gpg.gen_key(key_input)
        return key
        pass
    
    def export_keys(self, keyids):
        ascii_armored_public_keys = self.__gpg.export_keys(keyids) # same as gpg.export_keys(keyids, False)
        ascii_armored_private_keys = self.__gpg.export_keys(keyids, True) # True => private keys
        return (ascii_armored_public_keys, ascii_armored_private_keys)
        pass

    def list_keys(self, priv=False):
        return self.__gpg.list_keys(priv)
        pass

    def search(self, id, limit=1):
        '''
        return:
            keys:
                [{'keyid': u'92905378', 'uids': [u'Vinay Sajip <vinay_sajip@hotmail.com>'], 'expires': u'', 'length': u'1024', 'algo': u'17', 'date': u'1221156445', 'type': u'pub'}]
        '''
        keys = self.__gpg.search_keys(id, self.__keyserver)
        if len(keys) <= limit:
            return keys
        return keys[:limit]
        pass

    def delete(self, fingerprint, priv=False):
        if not priv:
            print('Public')
            self.__gpg.delete_keys(fingerprint)
        else:
            print('Private')
            self.__gpg.delete_keys(fingerprint, True, self.__passphrase)
            self.__gpg.delete_keys(fingerprint)
        pass

    def submit(self, keyid):
        self.__gpg.send_keys(self.__keyserver, keyid)
        pass
    
    def recv_by_uid(self, uid, limit=1):
        u_keys = self.search(uid, limit)
        keyids = []
        for key in u_keys:
            keyids.append(key['keyid'])
        if keyids:
            self.recv(keyids)
        return keyids

    def recv(self, keyids):
        '''
        keyids: keyid list
        '''
        results = []
        for keyid in keyids:
            for result in self.__gpg.recv_keys(self.__keyserver, keyid).results:
                results.append(result['fingerprint'])
        print(results)
        return results
        pass

    def sign(self, data):
        '''
        data: str | bytes
        return signed bytes
        '''
        if self.__passphrase != None:
            return self.__gpg.sign(data, keyid=self.__fingerprint, passphrase=self.__passphrase).data
        return self.__gpg.sign(data, keyid=self.__fingerprint).data
        pass

    def verify(self, sign_data, isFile=False):
        if not isFile:
            verified = self.__gpg.verify(sign_data)
            if verified.trust_level is not None and verified.trust_level >= verified.TRUST_FULLY:
                print('Trust level: %s' % verified.trust_text)
        return verified.trust_text
        pass


    def encrypt(self, data, recipient_key, sign=False):
        if sign:
            encrypted_data = self.__gpg.encrypt(data, recipient_key, sign=self.__fingerprint, passphrase=self.__passphrase)
        else:
            encrypted_data = self.__gpg.encrypt(data, recipient_key)
        return encrypted_data.data
        pass

    def decrypt(self, data, sign=False):
        if sign:
            decrypted_data = self.__gpg.decrypt(data, passphrase=self.__passphrase)
        else:
            decrypted_data = self.__gpg.decrypt(data)

        if decrypted_data.trust_level is not None and decrypted_data.trust_level >= decrypted_data.TRUST_FULLY:
            print('Trust level: %s' % decrypted_data.trust_text)
        return decrypted_data.data
        pass