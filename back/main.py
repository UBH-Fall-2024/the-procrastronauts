from flask import Flask, render_template
from flask_socketio import SocketIO
from markupsafe import escape
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

clients = {}

@app.route('/')
def home():
    return render_template('index.html')

@socketio.on('connect')
def test_connect(auth):
    print("socket connection")
    print(auth)
    socketio.emit('my response', {'data': 'Connected'})

@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')

@socketio.on('send')
def message(content):
    data = json.loads(content)
    if data['id'] not in clients:
        clients[data.id] = (data['loc']['lon'], data['loc']['lat'])
    out = {}
    out['from'] = data['id']
    out['msg'] =  escape(data['msg'])
    pl = json.dumps(out)
    for i, l in clients.items():
        socketio.emit('recieve', pl)

def client_disconnect(id):
    socketio.emit('disconnect', to=id)
    del clients[id]

def client_update():
    while True:
        for i, l in clients.items():
            try:
                loc = json.loads(socketio.call('status', timeout=120))
                clients[i] = (loc['lon'], loc['lat'])
            except TimeoutError:
                client_disconnect(i)
            
        socketio.sleep(3)

if __name__ == '__main__':
    socketio.start_background_task(client_update)
    socketio.run(app)