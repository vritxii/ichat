from imodules import gen_nounce, check_nounce

def Test_Nounce():
    email = 'nkdzt@foxmail.com'
    nounce = gen_nounce(email)
    print(nounce)
    print(check_nounce(email, nounce))

if __name__ == '__main__':
    Test_Nounce()
    pass