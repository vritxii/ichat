import sys, json, os

Debug = True

DEFAULT_SERVER_CONFIG = {
    'Server1':{
        'email':'781442859@qq.com',
        'password':'fzomvdkhsgifbdai'
    },
    'Server2':{
        'email':'2582783208@qq.com',
        'password':'kraithshfyqbecad'
    }
}

DEFAULT_CLIENT_CONFIG = {
    'Last':['2582783208@qq.com'],
    'Users':{
        '2582783208@qq.com':{
            'NickName': 'zhongtao',
            'Email': '2582783208@qq.com',
            'Email Pass': 'kraithshfyqbecad',
            'Server Email': '781442859@qq.com',
            'Server Addr': ''
        },
        '781442859@qq.com':{
            'NickName': 'fanjianzhong',
            'Email': '781442859@qq.com',
            'Email Pass': 'fzomvdkhsgifbdai',
            'Server Email': '2582783208@qq.com',
            'Server Addr': ''
        }
    }
}


def dump_config(config:dict, Daemon):
    '''
    dump config to file
    :param config:config dict
    :param Daemon:mode C | S
    :return:
    '''
    data = json.dumps(config)
    cur_path = os.getcwd()
    if Daemon == 'C':
        f = open(cur_path+'/config/client.cfg', 'w+')
        data = f.write(data)
        f.close()
    else:
        f = open(cur_path+'/config/server.cfg', 'w+')
        data = f.write(data)
        f.close()
    pass


def load_config(Daemon):
    '''
    Load config from file
    :param Daemon:C | s
    :return:config dict
    '''
    cur_path = os.getcwd()
    if Daemon == 'C':
        data = None
        path = cur_path+'/config/client.cfg'
        exist = os.path.isfile(cur_path)
        if exist:
            with open(path, 'r') as f:
                data = f.read()
        else:
            dump_config(DEFAULT_CLIENT_CONFIG, 'C')
            data = json.dumps(DEFAULT_CLIENT_CONFIG)
    else:
        data = None
        path = cur_path+'/config/server.cfg'
        exist = os.path.isfile(cur_path)
        if exist:
            with open(path, 'r') as f:
                data = f.read()
        else:
            dump_config(DEFAULT_SERVER_CONFIG, 'S')
            data = json.dumps(DEFAULT_SERVER_CONFIG)

    return json.loads(data)
    pass