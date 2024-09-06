from flask import Flask, request, jsonify, session
import os
import base64
import cv2 
import numpy as np 
import dlib
import face_recognition
import requests

#Database functions imported from database.py
from database import *

#function imported from texting.py. Used to text a caregiver.
from texting import phone_check, text_to_user
from faceRecognition import facial_recognition, extract_ids_from_url

app = Flask(__name__)
app.secret_key = 'FLFIJLIEFJSLIJALIJA556433'

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

        print('user_id: ', user_id)
        print('album_id: ', album_id)

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

    print('data:', data)
    
    # Ensure the required fields are present
    if not data or 'userID' not in data:
        return jsonify({'error': 'Invalid data'}), 400
    
    user_id = data['userID']

    print('userID: ', user_id)

    #Run function to change the notification setting for the esp32 cam
    temp = retrieve_all_albums(user_id)

    print('albumData: ', temp)

    #print(temp)

    if temp == 0:
        return jsonify({'message': 'Server failed to retrieve album data'}), 400
    
    # Convert albumIDs to integers
    album_data = {
        'albumID': [int(x) for x in temp['albumID']],
        'names': temp['names']
    }

    return jsonify(album_data), 200

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


@app.route('/obtain_credentials', methods=['POST'])
def obtain_credentials():

    try:

        # Retrieve JSON data from the request
        data = request.get_json()

        # Retrieves model number field for camera from json 
        camera_id = data.get('camera_id')

        #print('camera_id: ', camera_id)

        outcome = retrieve_user_id_by_model_number(camera_id)

        #Using the userID retrieve the phone number information

         # Check if the userID was found
        if outcome:
            # Prepare data to send in the POST request to /contacts_for_camera
            post_data = {'userID': outcome}
            
            # Make a POST request to /contacts_for_camera route
            response = requests.post('http://127.0.0.1:3002/contacts_for_camera', json=post_data)
            
            # Check the response status code and content
            if response.status_code == 200:
                contact_info = response.json()
                #print('Contact Info:', contact_info)
                caregiver_carrier = contact_info.get('caregiver_carrier')
                caregiver_phone = contact_info.get('caregiver_phone')
                patient_carrier = contact_info.get('patient_carrier')
                patient_phone = contact_info.get('patient_phone')    
                userID = outcome 

                '''
                print('caregiver_carrier: ', caregiver_carrier)
                print('caregiver_phone: ', caregiver_phone)
                print('patient_carrier: ', patient_carrier)
                print('patient_phone: ', patient_phone)
                '''
                
                return jsonify({'userID': userID, 'caregiver_phone_carrier': caregiver_carrier, 'caregiver_phone_number': caregiver_phone, 'patient_phone_carrier': patient_carrier, 'patient_phone_number': patient_phone}), 200
            else:
                print('Error retrieving contact information')
                return jsonify({'status': 'error', 'message': 'Failed to retrieve contact information'}), 500

        else:
            print('User ID not found for given camera_id')
            return jsonify({'status': 'error', 'message': 'User ID not found'}), 404
    
    except Exception as e:
        print(f"Error in recognize_face: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

#Facial reocngition post request
    
@app.route('/faceRecognize', methods=['POST'])
def recognizeFace():

    try:

        # Retrieve JSON data from the request
        data = request.get_json()

        # Extract base64 image data and user credentials
        base64_image = data.get('imageData')
        user_id = data.get('userID')

        caregiver_phone = data.get('caregiver_phone_number')
        patient_phone = data.get('patient_phone_number')
        caregiver_carrier = data.get('caregiver_carrier')
        patient_carrier = data.get('patient_carrier')

        print("caregiver_phone: ", caregiver_phone)
        print("patient_phone: ", patient_phone)
        print("caregiver_carrier: ", caregiver_carrier)
        print("patient_carrier: ", patient_carrier)

        user_id = int(user_id)

        if not base64_image or not user_id:
            return jsonify({"success": False, "message": "Failed to upload image"}), 400

        # Decode the base64 image data
        image_data = base64.b64decode(base64_image)

        # Convert the byte string into a NumPy array
        np_image = np.frombuffer(image_data, dtype=np.uint8)

        # Decode the NumPy array into an image
        image = cv2.imdecode(np_image, cv2.IMREAD_COLOR)

        #Temporary to see output -------------------------------------
        
        '''
        # Create a directory to store the images, based on the user_id
        save_directory = f"images/user_{user_id}"
        os.makedirs(save_directory, exist_ok=True)

        # Define the file name with the user_id and current timestamp
        file_path = os.path.join(save_directory, f"{user_id}_image.jpg")

        # Save the image using OpenCV
        success = cv2.imwrite(file_path, image)        
        '''
        #-----------------------------------------------------
        
        img_url_list = retrieve_all_user_photos(user_id)

        # Initialize a dictionary to keep count of matches per album
        match_counts = {}

        # Iterate through the list of image URLs
        for url in img_url_list:
            # Extract the album ID from the URL
            userID, albumID, photoID = extract_ids_from_url(url)  # This function should extract the album ID from the URL structure

            base = "images/"

            base_url = base + userID + "-" + albumID + "-" + photoID + ".png"

            # Download and decode the image
            photo_data = download_image(base_url)

            if not photo_data:
                continue

            np_photo_img = np.frombuffer(photo_data, np.uint8)
            stored_img = cv2.imdecode(np_photo_img, cv2.IMREAD_COLOR)

            # Perform facial recognition
            if facial_recognition(image, stored_img):
                if albumID not in match_counts:
                    match_counts[albumID] = 0
                match_counts[albumID] += 1
            
        # Determine the album with the most matches
        if match_counts:

            most_recognized_album_id = max(match_counts, key=match_counts.get)

            #Check whether texts are enabled

            enable_notifications_val = get_enable_notifications(user_id)

            if ((enable_notifications_val == "User does not exist") or (enable_notifications_val == "Notification setting not found")):
                return jsonify({'status': 'fail', 'message': 'Notifications is not enabled'})

            #Retrieve name and bio using userID and albumID
            album_data = get_album_data(user_id, most_recognized_album_id)

            bio = album_data['bio']
            name = album_data['name']

            #Test to patient number
            text_to_user(patient_phone, patient_carrier, name, bio)
            
            return jsonify({
                'status': 'success',
                'message': 'Face recognized',
                'album_id': most_recognized_album_id,
                'matches': match_counts[most_recognized_album_id]
        })
        else:
            return jsonify({'status': 'fail', 'message': 'No match found'})

    except Exception as e:
        print(f"Error in recognize_face: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == "__main__":
    #in ECE building 192.168.1.131
    #regurlar can leave blank or 172.25.0.121
    app.run(host = '192.168.1.167', port=3000, debug=True)