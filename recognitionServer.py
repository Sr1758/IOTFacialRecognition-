from flask import Flask, request, jsonify

from database import create_album, clean_album, retrieve_all_albums 
from database import add_photo, update_enable_notifications, delete_album
from texting import phone_check, text_to_user

app = Flask(__name__)

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

    print(temp)

    if temp == 0:
        return jsonify({'message': 'Server failed to retrieve album data'}), 400
    
    return jsonify(temp), 200

#If a user wants to add a photo to firebase storage then this method is called
@app.route('/addPhoto', methods=['POST'])
def addPhoto():

    # Get the JSON data from the request
    data = request.get_json()
    
    # Ensure the required fields are present
    if not data or 'img' not in data:
        return jsonify({'error': 'Invalid data'}), 400
    
    user_id = data['userID']
    album_id = data['albumID']

    temp = retrieve_all_albums(user_id,album_id)

    if temp == 0:
        return jsonify({'message': 'Server failed to retrieve album data'}), 400
    
    return jsonify(temp), 200

if __name__ == "__main__":
    app.run(port=3000, debug=True)