import pyrebase

config = {
    "apiKey": "AIzaSyBqDoFdN3zUZ2G4ke8QoBrjTylxrRBkhpg",
    "authDomain": "minglewise2019.firebaseapp.com",
    "databaseURL": "https://minglewise2019.firebaseio.com",
    "projectId": "minglewise2019",
    "storageBucket": "minglewise2019.appspot.com",
    "messagingSenderId": "316217858377",
    "appId": "1:316217858377:web:4a075efa015035ce4d2298",
    "measurementId": "G-4B2T0G8HKE"
}

firebase = pyrebase.initialize_app(config)
storage = firebase.storage()

CloudPath = "user-image-url/verify1.png"
LocalTests = "ImgTmpStore/AuthDP.png"

storage.child(CloudPath).download(LocalTests)