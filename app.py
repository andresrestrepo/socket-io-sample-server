#!/usr/bin/env python
from threading import Lock
from flask import Flask, session
from flask_socketio import SocketIO, emit


async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secreto'
socketio = SocketIO(app, async_mode=async_mode, cors_allowed_origins="*")
thread = None
thread_lock = Lock()


def background_thread():
    count = 1
    while True:
        socketio.sleep(10)
        count += 1
        socketio.emit('my_response',
                      {'data': 'Server generated event', 'count': count})


@socketio.on('my_event')
def test_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']})


@socketio.on('connect')
def test_connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(background_thread)
    emit('my_response', {'data': 'Connected', 'count': 0})


if __name__ == '__main__':
    socketio.run(app, debug=True)
