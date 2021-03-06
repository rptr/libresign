#
# This is the control panel backend.
# Using the development web server now but Flask is 
# apparently compatible with most/all web servers
#

import threading, logging, socket, subprocess, string

import request as requests
import flaskapp, config

# TODO wrap this up into a class

msg_queue   = None
running     = None
thread      = None
files       = []
signd       = None

def start(signd_, msgs):
    global msg_queue, running, thread, signd

    signd = signd_

    if not running:
        msg_queue = msgs
        running = True
        thread = threading.Thread(target=web_thread, args=())
        thread.setDaemon(True)
        thread.start()

def stop():
    # TODO use other server than werkzeug and deal with shutdown at that point
    pass

def web_thread():
    logging.info("starting web server")
    flaskapp.app.run(debug=True, use_reloader=False, threaded=True, port=config.HTTP_PORT, host="0.0.0.0")
    logging.info("stopping web server")

def push_request (request):
    if msg_queue:
        msg_queue.put(request)

def get_playlist ():
    return signd.get_playlist()

def get_all_files ():
    return signd.get_all_files()

def get_addr_1 ():
    # NOTE linux only -- best i could do
    p = subprocess.Popen(['hostname', '-I'], stdout=subprocess.PIPE)
    # TODO might be errors?
    addr, err = p.communicate()
    p.wait()

    # output of hostname something like "b'123.0.0.123 \n"
    addr = ''.join([c for c in str(addr) if c.isdigit() or c == '.'])

    return addr

# this works on Arch Linux ARM
def get_addr_pi ():
    # NOTE linux only -- best i could do
    p = subprocess.Popen(['ifconfig'], stdout=subprocess.PIPE)
    result, err = p.communicate()
    p.wait()

    iface = signd.net_iface
    found_iface = False

    addr = ""

    # regex knowledge would be useful...
    for line in str(result).split('\\n'):
        if found_iface:
            if line.find('inet ') >= 0:
                parts = [part for part in line.split(' ') if part != '']
                addr = parts[1]
                break

        if line.find(iface) >= 0:
            found_iface = True

    logging.debug("web::get_addr_pi(): got addr " + addr)

    return addr

def get_address ():
    port = config.HTTP_PORT
    addr = get_addr_1()

    if len(addr) == 0:
        addr = get_addr_pi()

    return 'http://' + addr + ':' + str(port) + '/'
