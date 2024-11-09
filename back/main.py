from flask import Flask, render_template
from flask_socketio import SocketIO
from markupsafe import escape
import json
import math
from octree import node, octree

RANGE = 12        #maximum distance for communication in meters
ER = 6366707.0195 #Earth Radius in Meters

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

clients = {}

# https://en.wikipedia.org/wiki/Haversine_formula
def haversine(p1, p2):
    a = math.sin(((p1[0]-p2[0])*math.pi/180)/2)**2
    b = math.cos(p1[0]*math.pi/180)
    c = math.cos(p2[0]*math.pi/180)
    d = math.sin(((p1[1]-p2[1])*math.pi/180)/2)**2
    return 2*ER*math.asin(math.sqrt(a+(b*c*d)))

def find_targets(id):
    n = clients[id]
    targets = []
    for i, o in clients:
        if haversine(n.get_pos(), o.get_pos()) < RANGE:
            targets.append(i)
    return targets

@app.route('/')
def home():
    return render_template('index.html')

# @socketio.on('connect')
# def test_connect(auth):
#     print("Client connected")

# @socketio.on('disconnect')
# def test_disconnect():
#     print('Client disconnected')

@socketio.on('send')
def message(content):
    data = json.loads(content)
    print(data)
    if data['id'] not in clients:
        clients[data['id']] = node(data['id'], data['lon'], data['lat'])
    out = {}
    out['from'] = data['id']
    out['msg'] =  escape(data['msg'])
    pl = json.dumps(out)
    targets = find_targets(data['id'])
    for t in targets:
        socketio.emit('receive', pl, to=t)

def client_disconnect(id):
    socketio.emit('disconnect', to=id)
    del clients[id]

def client_update():
    while True:
        for i, n in clients.items():
            try:
                loc = json.loads(socketio.call('status', timeout=120))
                clients[i] = (loc['lon'], loc['lat'])
            except TimeoutError:
                client_disconnect(i)
            
        socketio.sleep(3)

if __name__ == '__main__':
    socketio.start_background_task(client_update)
    socketio.run(app)