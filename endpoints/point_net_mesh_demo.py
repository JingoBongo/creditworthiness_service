import __init__
import cv2
from tensorflow import keras
from tensorflow.keras import layers
import mediapipe as mp
from blogic.transformers import FaceMeshCollecter, FaceMeshDrawer, Transformer
from blogic.point_net_api import *
from flask import render_template, redirect, url_for, request, Response
from utils import constants as c
from argparse import ArgumentParser
from utils import logger_utils as log
from utils.flask_child import FuseNode

parser = ArgumentParser()
app = FuseNode(__name__, template_folder=c.root_path + c.templates_folder_name, arg_parser=parser)

emotions = {
    0: 'Neutral',
    1: 'Happy',
    2: 'Sad',
    3: 'Surprise',
    4: 'Fear',
    5: 'Disgust',
    6: 'Anger',
    7: 'Contempt',
    8: 'Error'
}

video_capture = cv2.VideoCapture(0)
shown_image = None
model_predictions = None
first_degree, second_degree, third_degree, fourth_degree = 64, 128, 256, 512


def initialize_mediapipe_mesh():
    """Mesh extractor transformer that takes out of the image found landmarks

    Returns:
        Transformer: Transformer that 3D face landmarks extraction out of image
    """
    return FaceMeshCollecter(mp.solutions.face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1,
                                                             min_detection_confidence=0.75))


def initialized_mediapipe_mesh_drawer():
    """Mesh drawer Transformer object that writes found meshes right on the image

    Returns:
        Transformer: Transformer that draws 3D facial scan landmarks right on image
    """
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh_images = mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1,
                                             min_detection_confidence=0.75)
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles
    return FaceMeshDrawer(mp_face_mesh, face_mesh_images, mp_drawing, mp_drawing_styles)


def point_net_initialization(first_degree: int, second_degree: int,
                             third_degree: int, fourth_degree: int):
    """initialize point net model with specified layer depth parameters

    Args:
        first_degree (int): first degree depth
        second_degree (int): second degree depth
        third_degree (int): third degree depth
        fourth_degree (int): fourth degree depth

    Returns:
        keras.Model: base model, where weights should be loaded
    """
    inputs = keras.Input(shape=(468, 3))

    x = tnet(inputs, 3, first_degree, second_degree, third_degree, fourth_degree)
    x = conv_bn(x, 32)
    x = conv_bn(x, 32)

    x = tnet(x, 32, first_degree, second_degree, third_degree, fourth_degree)
    x = conv_bn(x, 32)
    x = conv_bn(x, first_degree)
    x = conv_bn(x, third_degree)

    x = layers.GlobalMaxPooling1D()(x)
    x = dense_bn(x, second_degree)
    x = layers.Dropout(0.4)(x)
    x = dense_bn(x, first_degree)
    x = layers.Dropout(0.4)(x)

    outputs = layers.Dense(8, activation="softmax")(x)

    model = keras.Model(inputs=inputs, outputs=outputs, name="pointnet")
    return model


def point_net_weights_load(model: keras.Model, path: str):
    """load weights of the model

    Args:
        model (keras.Model): point net model trained (make sure that loading model
                                is the same as you have initialized)
        path (str): where model weights are saved

    Returns:
        keras.Model: updated model with loaded weights
    """
    model.load_weights(path)
    return model


def gen():
    global model_predictions

    face_mesh_collecter = initialize_mediapipe_mesh()
    face_mesh_drawer = initialized_mediapipe_mesh_drawer()
    model = point_net_initialization(64, 128, 256, 512)
    model = point_net_weights_load(model, c.resources_folder_full_path + '\\better_v1_1_point_net\\')

    while not False:
        ret, image = video_capture.read()
        landmarked_image = face_mesh_drawer.transform(image)

        if landmarked_image is not None:
            shown_image = landmarked_image
        else:
            shown_image = image

        landmarks = face_mesh_collecter.transform(image)
        if landmarks is not None:
            model_predictions = model.predict(landmarks.reshape(1, 468, 3))
            print(model_predictions)

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + cv2.imencode('.jpg', shown_image)[1].tobytes() + b'\r\n')
    video_capture.release()


def pred():
    face_mesh_collecter = initialize_mediapipe_mesh()
    model = point_net_initialization(64, 128, 256, 512)
    model = point_net_weights_load(model, c.resources_folder_full_path + '\\better_v1_1_point_net\\')
    while not False:
        ret, image = video_capture.read()
        # landmarks = face_mesh_collecter.transform(image)
        # yield emotions.get(model_predictions.index(max(model_predictions)), 8)
        yield 'I am showing endpoints text'
        # return Response(emotions.get(predictions.index(max(predictions)), 8), mimetype='text')


@app.route('/demo')
def index():
    """Video streaming"""
    return render_template('index.html')


@app.route('/my_link')
def abobaboba():
    """Video streaminasdasdasdg"""
    return emotions.get(model_predictions.index(max(list(model_predictions)), 8))

@app.route('/ajax')
def ajax():
    """Video streaminasdasdasdg"""
    if type(model_predictions) is np.ndarray:
        llli = list(model_predictions[0])
        ind = llli.index(max(llli))
        ans = emotions.get(ind, 'error')

        return f"{ans} : {model_predictions}"
    return f"error getting result"

@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/emotion_feed')
def emotion_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(pred(), mimetype='text/event-stream')


@app.route('/pyscript')
def ijinja():
    """Landing page."""
    return render_template(
        'home.html'
    )


if __name__ == "__main__":
    app.run()
