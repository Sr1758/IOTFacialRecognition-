from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/addAlbum/', methods=['POST'])
def add_album():
    # Get the JSON data from the request
    data = request.get_json()
    
    # Ensure the required fields are present
    if data or 'userID' not in data or 'name' not in data or 'bio' not in data:
        return jsonify({'error': 'Invalid data'}), 400
    
    user_id = data['userID']
    name = data['name']
    bio = data['bio']

    '''
    Import a function from within the database.py file in
    order to handle creating a new album on a the firebase
    database. If the function executes sucessfully,
    then sucess a 200 sucess json message back to the
    app client. Otherwise, send a 400 error message.
    '''
    
    print(f'User ID: {user_id}, Album Name: {name}, Album Bio: {bio}')
    
    return jsonify({'message': 'Album added successfully'}), 200

@app.route('/enable_camera/', methods=['POST'])
def enable_camera():
    # Get the JSON data from the request
    data = request.get_json()
    
    # Ensure the required fields are present
    if not data or 'userID' not in data or 'enable_camera' not in data:
        return jsonify({'error': 'Invalid data'}), 400
    
    user_id = data['userID']
    camera_notification_switch = data['enable_camera']

    '''
    Import a function from within the database.py file
    that allows one to enable and diable text notifications
    from within the database. If the function executes sucessfully,
    then sucess a 200 sucess json message back to the
    app client. Otherwise, send a 400 error message.
    '''
    
    # Here, you can add logic to store the album in the database.
    # For now, we'll just print the data and return a success message.
    print(f'User ID: {user_id}, Notification switch: {camera_notification_switch}')
    
    return jsonify({'message': 'Album added successfully'}), 200

if __name__ == "__main__":
    app.run(port=3002, debug=True)