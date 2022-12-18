import __init__
import cv2
from flask import render_template, redirect, url_for, request, Response
from utils import constants as c
from argparse import ArgumentParser
from utils import logger_utils as log
from utils.flask_child import FuseNode

parser = ArgumentParser()
app = FuseNode(__name__, arg_parser=parser)

video_capture = cv2.VideoCapture(0)


def gen():
    while True:
        ret, image = video_capture.read()
        cv2.imwrite(c.temporary_files_folder_full_path + c.double_forward_slash + 't.jpg', image)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + open(
            c.temporary_files_folder_full_path + c.double_forward_slash + 't.jpg', 'rb').read() + b'\r\n')
    video_capture.release()


@app.route('/')
def index():
    """Video streaming"""
    return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


# below are just example endpoints, above is the jewel you are looking for, you might want to take a look at pyscript tho
@app.route('/send_n')
def send_n():
    return 'sus'


@app.route('/pyscript')
def ijinja():
    """Landing page."""
    return render_template(
        'home.html'
    )


@app.route('/index')
def indblablablaex():
    return 'Did you expect a default page or something? amogus'


@app.route('/snake')
def snake():
    """When pockets are empty.. at least you can play snakes
    ---
    responses:
      200:
        description: 99% caution
    """
    return render_template('snakes.html')


@app.route('/tetris')
def tetris():
    """This is becoming a common joke.. I like it
    ---
    responses:
      200:
        description: 99% caution
    """
    return render_template('tetris.html')


@app.route("/user/<string:str_variable>")
def endpoint_with_var(str_variable):
    """I have no idea why is this a title
        These are just notes as an example. We don't need most of this
        functionality, plus we aren't paid for this. So let's keep it
        simple as in hello_world endpoit, ey?
        ---
        parameters:
          - arg1: whatever, dude, this goes into business logic for now
            type: string
            required: true
            default: none, actually
        definitions:
          Job_id:
            type: String
        responses:
          200:
            description: A simple business logic unit with swagger
        """
    return 'elo hello fello\', %s' % str_variable


if __name__ == "__main__":
    app.run()
