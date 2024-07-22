import face_recognition
import cv2
import urllib.request
import numpy as np
import os
from dotenv import load_dotenv
import math
import sys


#Load environmental variables from .env file
load_dotenv()

def retrieve_camera_ip():

    '''
    Temporary environmental variable to store the ip address of the camera server.
    In future code, the ip address will be sent to the subordinate facial recognition server
    through the camera's own http post request.
    '''

    camera_ip = os.environ['CAMERA_IP']
    #print(camera_ip)
    return camera_ip

if __name__ == '__main__':

    camera_ip = retrieve_camera_ip()

    #Replace the URL with the IP camera's stream URL
    url = 'http://' + camera_ip + '/cam-lo.jpg'
    cv2.namedWindow("live Cam Testing", cv2.WINDOW_AUTOSIZE)

    #Create a VideoCapture object
    cap = cv2.VideoCapture(url)

    #Check if the IP camera stream is opened successfully
    if not cap.isOpened():
        print("Failed to open the IP camera stream")
        exit()

    #Read and display video frames
    while True:
        #Read a frame from the video stream
        img_resp=urllib.request.urlopen(url)
        imgnp=np.array(bytearray(img_resp.read()), dtype=np.uint8)
        #ret, frame = cap.read()
        im = cv2.imdecode(imgnp,-1)

        cv2.imshow('live Cam Testing', im)
        key=cv2.waitKey(5)
        if key==ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows