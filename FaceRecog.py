
import os
from matplotlib import pyplot as plt
import cv2
import face_recognition as fr


#Function logic checked
#Accepted to build on
#Displaying image when path is passed in this function

def ShowPic(img):
    img = cv2.imread(img, 0)
    plt.imshow(img, cmap = 'gray', interpolation = 'bicubic')
    plt.xticks([]), plt.yticks([])  # to hide tick values on X and Y axis
    plt.show()

#Function logic checked
#Accepted to build on
#Load, Encode, amd compare for single user

def SelfieAuth(auth_image, new_image):
    user_given_image = fr.load_image_file(auth_image)
    user_selfie_image = fr.load_image_file(new_image)

    try:
        user_encoding = fr.face_encodings(user_given_image)[0]
        selfie_encoding = fr.face_encodings(user_selfie_image)[0]
    except Exception as e:
        print("Error : ", e)
        ShowPic(new_image)
        return False

    result = fr.compare_faces([user_encoding], selfie_encoding)
    ShowPic(new_image)
    return result


#Calling defined function

#/home/dark-flash/code/dating Ai/Facial_recognition/data/Aastha Doshi/Aastha1.jpg
#/home/dark-flash/code/dating Ai/Facial_recognition/data/Helma/Helma1.jpg
#/home/dark-flash/code/dating Ai/Facial_recognition/data/Hardik Vij/Hardik1.jpg


# In[ ]:




