from flask import Flask, request, jsonify

from database import *
from texting import phone_check, text_to_user

app = Flask(__name__)


##########################################################################################
# Method's in this section create and delete users

@app.route('/createUser', methods=['POST'])
def create_user():
    # Get the JSON data from the request
    data = request.get_json()

    #Package data for usage in create_album function
    user_id = data['userID']

    # Error messages
    # Ensure the required fields are present
    if not data or 'userID' not in data:
        return jsonify({'error': 'Invalid data'}), 400

    # Check if the user already exists
    if check_user_exists(user_id):
        return jsonify({'error': 'User already exists'}), 400
    
    # database structure
    user_info = {
        "userID": user_id,
        "enableNotifications": True,
        "numAlbums": 0,
        "albums": {}
    }

    # Create the user account in the database
    test = create_user_account(user_id, user_info)

    if test==1:
        return jsonify({'message': 'User created successfully'}), 200
    else:
        return jsonify({'message': 'Unknown error'}), 400
    



# NOTE ONCE A USER IS DELETE IT'S GONE FOREVER
@app.route('/deleteUser', methods=['POST'])
def delete_single_user():
    # Get the JSON data from the request
    data = request.get_json()

    # Ensure the required fields are present
    if not data or 'userID' not in data:
        return jsonify({'error': 'Invalid data'}), 400

    user_id = data['userID']

    # Attempt to delete the user
    result = delete_user(user_id)

    if result == 1:
        return jsonify({'message': 'User deleted successfully'}), 200
    elif result == "User does not exist":
        return jsonify({'message': 'User does not exist'}), 400
    else:
        return jsonify({'message': 'Failed to delete user'}), 400

    


##########################################################################################
# Method's in this section is related to Adding/Deleting/Reading Albums


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
        return jsonify({'message': 'Cannot have more than 10 albums per user'}),400
    elif test=="User does not exist":
        return jsonify({'message': 'User does not exist'}),400
    else:
        return jsonify({'message': 'Unknown error'}), 400




@app.route('/deleteAlbum', methods=['POST'])
def delete_album_endpoint():
    data = request.get_json()
    
    if not data or 'userID' not in data or 'albumID' not in data:
        return jsonify({'error': 'Invalid data'}), 400
    
    user_id = data['userID']
    album_id = data['albumID']

    result = delete_album(user_id, album_id)

    if result == 1:
        return jsonify({'message': 'Album deleted successfully'}), 200
    elif result == "Could not clean album":
        return jsonify({'message': 'Could not clean album'}), 400
    elif result == "Album does not exist":
        return jsonify({'message': 'Album does not exist'}), 400
    else:
        return jsonify({'message': 'Unknown error'}), 400
    

#When a user requests a list of all the albums currently on firebase for a user this method is called
@app.route('/getAlbums', methods=['POST'])
def getAlbums():

    # Get the JSON data from the request
    data = request.get_json()
    
    # Ensure the required fields are present
    if not data or 'userID' not in data:
        return jsonify({'error': 'Invalid data'}), 400
    
    user_id = data['userID']

     # Check if the user doesn't exists
    if not check_user_exists(user_id):
        return jsonify({'error': 'User does not exists'}), 400

    #Run function to change the notification setting for the esp32 cam
    temp = retrieve_all_albums(user_id)

    print(temp)

    if temp == 0:
        return jsonify({'message': 'Server failed to retrieve album data'}), 400
    
    return jsonify(temp), 200



###########################################################################################
# Method's in this section is related to Adding/Deleting/Reading photo's

#If a user wants to add a photo to firebase storage then this method is called
@app.route('/addPhoto', methods=['POST'])
def addPhoto(): 
    # Get the JSON data from the request
    data = request.get_json()
    
    # Ensure the required fields are present
    if not data or 'userID' not in data or 'albumID' not in data or 'img' not in data:
        return jsonify({'error': 'Invalid data'}), 400
    
    user_id = data['userID']
    album_id = data['albumID']
    img_path = data['img']

    # Check if the user exists
    user_ref = db.reference(f'users/{user_id}')
    user_data = user_ref.get()
    
    if not user_data:
        return jsonify({'error': 'User does not exist'}), 400
    
    # Check if the album exists
    album_ref = db.reference(f'users/{user_id}/albums/{album_id}')
    album_data = album_ref.get()
    
    if not album_data:
        return jsonify({'error': 'Album does not exist'}), 400

    # Retrieve the current number of images in the album
    num_images = album_data.get('numImages', 0)
    
    # Generate the new image ID
    image_id = num_images + 1
    
    # Create the storage path for the image
    storage_image_path = f'{user_id}-{album_id}-{image_id}.jpg'
    
    # Add the photo using the add_photo function
    result = add_photo(user_id, album_id, img_path, storage_image_path)
    
    if result == 0:
        return jsonify({'message': 'Failed to add photo'}), 400
    
    return jsonify({'message': 'Photo added successfully'}), 200





###########################################################################################
# Method's in this section controls the camera/face cam

#When user hits enable/disable notifications, this route is used to update the val of notications variable
@app.route('/camera_notifications', methods=['POST'])
def camera_notification_settings():
    # Get the JSON data from the request
    data = request.get_json()
    
    # Ensure the required fields are present
    if not data or 'userID' not in data:
        return jsonify({'error': 'Invalid data'}), 400
    
    user_id = data['userID']

    # Retrieve the current value of enableNotifications
    user_ref = db.reference(f'users/{user_id}')
    user_data = user_ref.get()

    if not user_data or 'enableNotifications' not in user_data:
        return jsonify({'error': 'User data not found or incomplete'}), 400

    # Toggle the enableNotifications value
    current_value = user_data['enableNotifications']
    new_value = not current_value

    # Update the value in the database
    update_enable_notifications(user_id, new_value)
    
    return jsonify({'message': f'Notification switched to {"enabled" if new_value else "disabled"}'}), 200



#Call this to turn on the facial recoginition camera
@app.route('/camera_on', methods=['POST'])
def camera_on():
    data = request.get_json()

    if not data or 'userID' not in data:
        return jsonify({'error': 'Invalid data'}), 400
    
    user_id = data['userID']
    
    # Step 1: Populate the faces folder
    populate_faces_folder(user_id)

    # Step 2: Start the camera
    subprocess.Popen(['python', 'main.py'])  #run's main.py

    return jsonify({'message': 'Camera is now on'}), 200


#######################################################################################
# This section is for helpful dev tools


@app.route('/getUserStructure', methods=['POST'])
def get_user_structure():
    # Get the JSON data from the request
    data = request.get_json()

    # Ensure the required fields are present
    if not data or 'userID' not in data:
        return jsonify({'error': 'Invalid data'}), 400

    user_id = data['userID']

    # Retrieve the full user structure from Firebase
    user_data = retrieve_user_structure(user_id)

    if user_data is None:
        return jsonify({'error': 'User does not exist'}), 400

    return jsonify(user_data), 200



if __name__ == "__main__":
    app.run(port=3000, debug=True)