import FaceRecog
from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def frc():
    auth_image = "X:/dating Ai/Facial_recognition/data/Ishan Sir/Ishan1.jpg"
    new_image = "X:/dating Ai/Facial_recognition/data/Ishan Sir/Ishan2.jpg"
    return FaceRecog.SelfieAuth(auth_image, new_image), 200



if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))