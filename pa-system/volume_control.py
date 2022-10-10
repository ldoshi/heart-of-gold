import subprocess
import flask

def _increase_volume():
    subprocess.run(["amixer", "-D", "pulse", "sset", "Master", "5%+"])

def _decrease_volume():
    subprocess.run(["amixer", "-D", "pulse", "sset", "Master", "5%-"])

app = flask.Flask(__name__)

@app.route('/', methods=['GET'])
def volume_control():
    volume_direction = flask.request.args.get('volume-direction')
    if volume_direction is not None:
        if volume_direction == 'up':
            _increase_volume()
        if volume_direction == 'down':
            _decrease_volume()
            
    return flask.render_template('volume_control.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0')
