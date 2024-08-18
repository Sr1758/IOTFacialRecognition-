from flask import Flask, request, jsonify
import os
import base64
import cv2 
import numpy as np 
import dlib
import face_recognition
from database import create_album, clean_album, retrieve_all_albums 
from database import add_photo, update_enable_notifications, delete_album
from database import updateCamera, validate_model_number
from texting import phone_check, text_to_user

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload_image():
    try:
        # Retrieve JSON data from the request
        data = request.get_json()

        # Extract base64 image data
        base64_image = data.get('imageData')
        user_id = data.get('userID')
        album_id = data.get('albumID')

        user_id = int(user_id)
        album_id = int(album_id)

        if not base64_image or not user_id or not album_id:
            return jsonify({"success": False, "message": "Failed to upload image"}), 400

        # Decode the base64 image data
        image_data = base64.b64decode(base64_image)

        # Convert the byte string into a NumPy array
        np_image = np.frombuffer(image_data, dtype=np.uint8)

        # Decode the NumPy array into an image
        image = cv2.imdecode(np_image, cv2.IMREAD_COLOR)

        '''
        Check if there is a SINGULAR face in the image. If there is a single page, then proceed to store image.
        * There is more than one face or there is no face. Give json error response message.
        '''

        # Use face_recognition to locate faces
        face_locations = face_recognition.face_locations(image)

        # Check the number of detected faces
        if len(face_locations) != 1:
            return jsonify({"success": False, "message": "Image must contain exactly one face"}), 400

        # Get the path to the OpenCV package installation
        opencv_path = os.path.dirname(cv2.__file__)

        # Construct the path to the Haar Cascades directory
        haar_cascades_path = os.path.join(opencv_path, 'data', 'haarcascade_frontalface_default.xml')
        
       # Load the pre-trained face detection model (Haar Cascade)

        face_cascade = cv2.CascadeClassifier(haar_cascades_path)

        # RGB to grayscale 
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) 

        #Improves contrast of grayscale image
        gray = cv2.equalizeHist(gray)

        #Reduce noice before detection
        gray = cv2.GaussianBlur(gray, (5, 5), 0)

        # Detect faces in the image

        '''
        Change these variables so that face detector is more sensitive (or figure out how to set up 
        facial_reocgnition library for ML facial recognition)
        '''

        # uses face_recognition (deep learning) 
        faces = face_recognition.face_locations(image)
        
        #uses haar cascades

        '''
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
 
        print("faces: ")
        print(len(faces))
    
        # Post-process to filter out false positives
        filtered_faces = []
        for (x, y, w, h) in faces:
            aspect_ratio = w / float(h)
            if 0.75 < aspect_ratio < 1.3: 
                filtered_faces.append((x, y, w, h))

        faces = filtered_faces

        print("filtered face number: ")
        print(len(faces))

        '''

        print("filtered face number: ")
        print(len(faces))
        
        if len(faces) != 1:
            return jsonify({"success": False, "message": "Image must contain exactly one face"}), 400
        

        # Define local and storage paths
        local_image_path = f"/tmp/{user_id}-{album_id}.png"

        # Save the image temporarily to local file system
        with open(local_image_path, "wb") as image_file:
            image_file.write(image_data)

        # Call the add_photo function to upload the image
        result = add_photo(user_id, album_id, local_image_path)

        # Remove the temporary local image file
        os.remove(local_image_path)

        if result == 1:
            return jsonify({"success": True, "message": "Image uploaded successfully"}), 200
        else:
            return jsonify({"success": False, "message": "Failed to upload image"}), 400
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
@app.route('/deleteAlbum', methods=['POST'])
def deleteAlbum():
    try:
        # Retrieve JSON data from the request
        data = request.get_json()

        # Extract userID and albumID string data
        user_id = data.get('userID')
        album_id = data.get('albumID')

        user_id = int(user_id)
        album_id = int(album_id)

        if  not user_id or not album_id:
            return jsonify({"success": False, "message": "Data could not be properly retrieved"}), 400
        
        res = delete_album(user_id, album_id)

        if res!=1:
            print(res)
            return jsonify({"success": False, "message": "Data could not be sucessfully cleaned or deleted"}), 400
        
        return jsonify({"success": True, "message": "Images and metadata succesfully deleted"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400
    

@app.route('/clearAlbum', methods=['POST'])
def clearAlbum():
    try:
        # Retrieve JSON data from the request
        data = request.get_json()

        # Extract userID and albumID string data
        user_id = data.get('userID')
        album_id = data.get('albumID')

        user_id = int(user_id)
        album_id = int(album_id)

        if  not user_id or not album_id:
            return jsonify({"success": False, "message": "Data could not be properly retrieved"}), 400
        
        res = clean_album(user_id,album_id)

        if res!=1:
            print(res)
            return jsonify({"success": False, "message": "Image data could not be sucessfully cleaned"}), 400
        
        return jsonify({"success": True, "message": "Images successfully deleted"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400

#This method is used to add an album to a user's account
@app.route('/addAlbum', methods=['POST'])
def add_album():
    # Get the JSON data from the request
    data = request.get_json()
    
    #Package data for usage in create_album function
    user_id = data['userID']
    name = data['name']
    bio = data['bio']

    # Ensure the required fields are present
    if not data or 'userID' not in data or 'name' not in data or 'bio' not in data:
        return jsonify({'error': 'Invalid data'}), 400

    album_info = {
        'name': name,
        'bio': bio,
        'numImages': 0
    }

    #Create an album for a user on the real time database 
    test = create_album(user_id, album_info)

    if test==1:
        return jsonify({'message': 'Album added successfully'}), 200
    elif test=="Cannot have more than 10 albums per user":
        return jsonify({'message': 'Cannot have more thatn 10 albums per user'}),400
    elif test=="User does not exist":
        return jsonify({'message': 'User does not exist'}),400
    else:
        return jsonify({'message': 'Unknown error'}), 400

#When user hits enable/disable notifications, this route is used to update the val of notications variable
@app.route('/enable_camera', methods=['POST'])
def enable_camera():

    # Get the JSON data from the request
    data = request.get_json()
    
    # Ensure the required fields are present
    if not data or 'userID' not in data or 'enable_camera' not in data:
        return jsonify({'error': 'Invalid data'}), 400
    
    user_id = data['userID']
    camera_notification_switch = data['enable_camera']

    #Run function to change the notification setting for the esp32 cam
    update_enable_notifications(user_id,camera_notification_switch)
    
    return jsonify({'message': 'Notification Switched'}), 200


#When a user requests a list of all the albums currently on firebase for a user this method is called
@app.route('/getAlbums', methods=['POST'])
def getAlbums():

    # Get the JSON data from the request
    data = request.get_json()
    
    # Ensure the required fields are present
    if not data or 'userID' not in data:
        return jsonify({'error': 'Invalid data'}), 400
    
    user_id = data['userID']

    #Run function to change the notification setting for the esp32 cam
    temp = retrieve_all_albums(user_id)

    #print(temp)

    if temp == 0:
        return jsonify({'message': 'Server failed to retrieve album data'}), 400
    
    return temp, 200

#This method is used to register a camera model number to a specific account
@app.route('/cam_model', methods=['POST'])
def update_cam_model_number():

    # Get the JSON data from the request
    data = request.get_json()
    
    #Package data for usage in create_album function
    user_id = data['userID']
    modelNumber = data['cameraModel']

    # Ensure the required fields are present
    if not data or 'userID' not in data or 'cameraModel' not in data:
        return jsonify({'error': 'Invalid data'}), 400
    
    #Check whether there is already an account with the specified model number
    temp = validate_model_number(user_id, modelNumber)

    if temp == "Another user already has this model number":
        jsonify({'message': 'Another user already has this model number'}), 400
    elif temp == 1:
        test = updateCamera(user_id,modelNumber)
    else:
        return jsonify({'message': 'Unknown error'}), 400

    #Check whether update was successful
    if test==1:
        return jsonify({'message': 'Camera model number updated successfully'}), 200
    else:
        return jsonify({'message': 'Unknown error'}), 400


if __name__ == "__main__":
    app.run(port=3000, debug=True)