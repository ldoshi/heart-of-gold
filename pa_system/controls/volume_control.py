import subprocess
import flask

_PACTL_COMMAND = ["pactl", "set-sink-volume", "@DEFAULT_SINK@"]

def _increase_volume():
    subprocess.run(_PACTL_COMMAND + ["+10%"])

def _decrease_volume():
    subprocess.run(_PACTL_COMMAND + ["-10%"])

app = flask.Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def volume_control():
    volume_direction = flask.request.form.get('volume-direction')
    if volume_direction is not None:
        if volume_direction == 'up':
            _increase_volume()
        if volume_direction == 'down':
            _decrease_volume()
            
    return flask.render_template('volume_control.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0')
