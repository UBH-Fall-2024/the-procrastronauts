from flask import Flask, render_template
from flask_socketio import SocketIO
from markupsafe import escape

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

@socketio.on('message')
def message(data):
    for i, l in clients.items():
        socketio.send(f'Anon: {escape(data.msg)}')

if __name__ == '__main__':
    socketio.run(app)