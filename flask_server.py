from flask import Flask, render_template, send_from_directory
from flask_socketio import SocketIO, emit
import os
from datetime import datetime
import time

app = Flask(__name__)
socketio = SocketIO(app)

# Directory where pictures are stored
PICTURES_DIR = "pictures"

@app.route('/')
def index():
    """Display a list of all pictures."""
    if not os.path.exists(PICTURES_DIR):
        os.makedirs(PICTURES_DIR)

    pictures = []
    for root, dirs, files in os.walk(PICTURES_DIR):
        for file in files:
            if file.endswith('.jpg'):
                # Build relative path for each file
                file_path = os.path.relpath(os.path.join(root, file), PICTURES_DIR)
                pictures.append(file_path)

    pictures.sort(key=lambda x: datetime.strptime("_".join(x.split('_')[1:]), '%Y_%m_%d_%H%M%S.jpg'))
    return render_template('index.html', pictures=pictures)

@app.route('/pictures/<path:filename>')
def picture(filename):
    """Serve a specific picture."""
    file_path = os.path.join(PICTURES_DIR, filename)
    if not os.path.exists(file_path):
        return "File not found", 404
    return send_from_directory(PICTURES_DIR, filename)

def monitor_directory():
    """Monitor the directory for new or deleted files."""
    existing_files = set(os.listdir(PICTURES_DIR))
    while True:
        time.sleep(2)  # Check every 2 seconds
        current_files = set(os.listdir(PICTURES_DIR))
        new_files = current_files - existing_files
        deleted_files = existing_files - current_files

        # Notify clients about new files
        for new_file in new_files:
            if new_file.endswith('.jpg'):
                socketio.emit('new_picture', {'filename': new_file})

        # Notify clients about deleted files
        for deleted_file in deleted_files:
            if deleted_file.endswith('.jpg'):
                socketio.emit('delete_picture', {'filename': deleted_file})

        existing_files = current_files

@socketio.on('connect')
def handle_connect():
    """Send the current pictures to the client upon connection."""
    pictures = []
    for root, dirs, files in os.walk(PICTURES_DIR):
        for file in files:
            if file.endswith('.jpg'):
                file_path = os.path.relpath(os.path.join(root, file), PICTURES_DIR)
                pictures.append(file_path)
    pictures.sort(key=lambda x: datetime.strptime("_".join(x.split('_')[1:]), '%Y_%m_%d_%H%M%S.jpg'))
    emit('initial_pictures', {'pictures': pictures})

if __name__ == '__main__':
    socketio.start_background_task(target=monitor_directory)
    socketio.run(app, debug=True)
