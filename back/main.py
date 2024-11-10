from flask import Flask, render_template, request
from flask_socketio import SocketIO
from markupsafe import escape
import json
import math
from octree import node, octree, quadtree

RANGE = 24        #maximum distance for communication in meters
ER = 6366707.0195 #Earth Radius in Meters

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

clients = {}

# tree = octree(0, 0, 0, ER*1.1)
tree = quadtree(0,0, 1)

USETREE = False

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
    if USETREE:
        targets = tree.find(n.get_pos())
        print(f'found {len(targets)} nearby {n.get_coord()} {n.id}')
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
    clients[request.sid].remove()
    del clients[request.sid]


@socketio.on('join')
def join(content):
    data = json.loads(content)
    if data['id'] not in clients:
        clients[data['id']] = node(data['id'], data['lat'], data['lon'])
    if USETREE:
        clients[data['id']].remove()
        tree.insert(clients[data['id']])

@socketio.on('send')
def message(content):
    data = json.loads(content)
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

@socketio.on('status')
def update(content):
    data = json.loads(content)
    if data['id'] not in clients:
        clients[data['id']] = node(data['id'], data['lat'], data['lon'])
    clients[data['id']].update_location(data['lat'], data['lon'])
    if USETREE:
        clients[data['id']].remove()
        tree.insert(clients[data['id']])
    socketio.emit('nearby', json.dumps({'count': len(find_targets(data['id']))-1}), to=data['id'])

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', ssl_context='adhoc')