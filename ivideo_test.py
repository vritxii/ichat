import sys
from ivideo import *
sys.path.append('./')

if __name__ == '__main__':
    run_type = sys.argv[1]
    port = int(sys.argv[2])
    if run_type == 'c':
        ac = Vid(Default_Host, port)
        ac.run()
    else:
        a_s = Audio_Server(Default_Host, port)
        a_s.run()
