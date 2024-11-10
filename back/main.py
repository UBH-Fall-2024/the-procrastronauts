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

tree = octree(0, 0, 0, ER*1.1)

USETREE = True

# https://en.wikipedia.org/wiki/Haversine_formula
def haversine(p1, p2):
    a = math.sin(((p1[0]-p2[0])*math.pi/180)/2)**2
    b = math.cos(p1[0]*math.pi/180)
    c = math.cos(p2[0]*math.pi/180)
    d = math.sin(((p1[1]-p2[1])*math.pi/180)/2)**2
    return 2*ER*math.asin(math.sqrt(a+(b*c*d)))

def find_targets(id):
    print(clients)
    n = clients[id]
    targets = []
    if USETREE:
        targets = tree.find(n.get_pos())
    else:
        for i, o in clients.items():
            dist = haversine(n.get_coord(), o.get_coord())
            print (f"people are {dist}m apart")
            if  dist < RANGE:
                targets.append(i)
    return targets

@app.route('/')
def home():
    return render_template('index.html')

@socketio.on('connect')
def test_connect(auth):
    print("Client connected")

@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')

@socketio.on('join')
def join(content):
    data = json.loads(content)
    print(data)
    if data['id'] not in clients:
        clients[data['id']] = node(data['id'], data['lat'], data['lon'])
    if USETREE:
        clients[data['id']].remove()
        tree.insert(clients[data['id']])

@socketio.on('send')
def message(content):
    data = json.loads(content)
    print(data)
    if data['id'] not in clients:
        clients[data['id']] = node(data['id'], data['lat'], data['lon'])
    if USETREE:
        clients[data['id']].remove()
        tree.insert(clients[data['id']])
    out = {}
    out['from'] = data['id']
    out['msg'] =  escape(data['msg'])
    pl = json.dumps(out)
    targets = find_targets(data['id'])
    for t in targets:
        socketio.emit('receive', pl, to=t)

def client_disconnect(id):
    socketio.emit('disconnect', to=id)
    clients[id].remove()
    del clients[id]

def client_update():
    while True:
        for i, n in clients.items():
            try:
                loc = json.loads(socketio.call('status', json.dumps({'count': len(find_targets(i))-1}), timeout=120, to=i))
                n.update_location(loc['lat'], loc['lon'])
                if USETREE:
                    n.remove()
                    tree.insert(n)
            except TimeoutError:
                client_disconnect(i)
            
        socketio.sleep(3)

if __name__ == '__main__':
    socketio.start_background_task(client_update)
    socketio.run(app, host='0.0.0.0', ssl_context='adhoc')