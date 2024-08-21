import firebase_admin
import subprocess
import os
import shutil
from firebase_admin import db, credentials, storage

#authenticate to firebase
cred = credentials.Certificate("credentials.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://ios-alzheimers-app-default-rtdb.firebaseio.com/',
    'storageBucket': 'ios-alzheimers-app.appspot.com'
})




'''
Check if the User ID is already being used/exists
'''

def check_user_exists(user_id):
    ref = db.reference('users')
    user_ref = ref.child(user_id)
    return user_ref.get() is not None


'''
Uses realtime database to store account data.
user_id: identifies each user (the userID key found on the mysql database)
user_info: json file that contains fields for a user entity

user_info:{
    "userID": INT
    "enableNotifications": BOOL
    "numAlbums": INT
}
'''
def create_user_account(user_id, user_info):
    ref = db.reference('users')
    user_ref = ref.child(user_id)
    user_ref.set(user_info)
    return 1

'''
Method to delete a User
'''

def delete_user(user_id):
    # Reference to the specific user's data
    user_ref = db.reference(f'users/{user_id}')
    
    # Check if the user exists
    user_data = user_ref.get()
    
    if not user_data:
        return "User does not exist"

    try:
        # Delete the user's data from the database
        user_ref.delete()
        return 1
    except Exception as e:
        print(f"Error occurred while deleting user: {e}")
        return "Failed to delete user"



'''
Uses realtime database to store album data.
album_id: identifies each album 
album_info: json file that contains fields for a user entity

album_info:{
    "albumID": INT
    "name": VARCHAR(256)
    "bio": VARCHAR(500)
    "numImages": INT
}
'''

def create_album(user_id, album_info):
    
    # Reference to the specific user's data
    user_ref = db.reference(f'users/{user_id}')
    
    # Get the user's current data
    user_data = user_ref.get()
    
    if not user_data:
        return "User does not exist"

    # Check the number of albums
    if 'numAlbums' not in user_data:
        number_of_albums = 0
    else:
        number_of_albums = user_data['numAlbums']

    if number_of_albums >= 10:
        return "Cannot have more than 10 albums per user"

    # Reference to the user's albums collection
    albums_ref = user_ref.child('albums')

    # Increment the number of albums
    updated_album_number = number_of_albums+1

    user_ref.update({
        'numAlbums': updated_album_number
    })

    # Create a new album
    album_id = str(updated_album_number)
    album_info['albumID'] = album_id  # Ensure the albumID field is included
    albums_ref = user_ref.child('albums')
    album_ref = albums_ref.child(album_id)
    album_ref.set(album_info)

    return 1

'''
Retrieves all albumID and name data from each album from the database
'''
def retrieve_all_albums(user_id):
    # Reference to the specific user's albums
    albums_ref = db.reference(f'users/{user_id}/albums')
    albums_data = albums_ref.get()

    if albums_data is None:
        return {
            'albumID': [],
            'names': []
        }

    names = []
    albumID = []

    # Check if albums_data is a list
    if isinstance(albums_data, list):
        for album in albums_data:
            if album:  # Skip null entries
                names.append(album['name'])
                albumID.append(album['albumID'])
    else:
        print("Unexpected structure for albums_data")
        return {
            'albumID': [],
            'names': []
        }

    album_collection = {
        'albumID': albumID,
        'names': names
    }

    return album_collection



'''
Used to update value of enableNotifications for a single user
'''
def update_enable_notifications(user_id, notification_val):

    user_ref = db.reference(f'users/{user_id}')
    
    # Get the current user data
    user_data = user_ref.get()
    
    if not user_data:
        return "User data does not exist"

    user_ref.update({
        'enableNotifications': notification_val
    })

    return 1

'''
Function used to add an image to an album. Images are stored in Storage on firebase

local_image_path: 

the location of an image file on your computer

storage_image_path: 

where you want to store the image in firestore and what name it will go under

name of image should be userID-albumID-image#.png/jpeg
'''
def add_photo(user_id, album_id, local_image_path, storage_image_path):

    # Reference to storage
    bucket = storage.bucket()

    # Reference to the album
    album_ref = db.reference(f'users/{user_id}/albums/{album_id}')
    data = album_ref.get()

    if 'numImages' not in data:
        print("There is no numImages field in this album")
        return 0
    elif data['numImages'] >= 20:
        print("Number of images exceeds limit for individual album")
        return 0
    else:
        num_images = data['numImages']

    # Increment image count to get the new image ID
    img_id = num_images + 1

    # Construct the image's unique name
    img_name = f"{user_id}-{album_id}-{img_id}"

    # Upload the image to Firebase Storage
    blob = bucket.blob(storage_image_path)
    blob.upload_from_filename(local_image_path)

    # Reference to the image list in the album
    images_ref = album_ref.child('images')

    # Add the new image information to the database
    image_info = {
        'imageID': img_id,
        'imageName': img_name,
        'storagePath': storage_image_path
    }

    images_ref.child(str(img_id)).set(image_info)

    # Update the number of images in the album
    album_ref.update({
        'numImages': img_id
    })

    print(f"Image {img_name} added successfully to album {album_id} for user {user_id}")

    return 1


'''
Clean out all the images within an album.
'''
def clean_album(user_id, album_id):
    try:
        path = 'images/'
        bucket = storage.bucket()

        # Character array used to sort the image list for the images that correspond to a particular user's album
        sorting_by_name = f'{user_id}-{album_id}'

        # Lists location of all images that correspond to the a particular album
        blobs = list(bucket.list_blobs(prefix=sorting_by_name))
        print(f"Blobs found: {blobs}")

        # If no images found under user and album specified to check
        if not blobs:
            print(f"No files found under user_id {user_id} and album_id {album_id}")
            return "No files found under user_id and album_id given"

        # Delete every image that corresponds to that user and album
        for blob in blobs:
            print(f"Deleting blob: {blob.name}")
            blob.delete()

        album_ref = db.reference(f'users/{user_id}/albums/{album_id}')
        album_ref.update({'numImages': 0})
        print(f"Album {album_id} for user {user_id} cleaned successfully")

        return 1
    except Exception as e:
        print(f"An error occurred while cleaning album {album_id} for user {user_id}: {e}")
        return "Unknown error"


'''
Delete album images and album entity in realtime database
'''
def delete_album(user_id, album_id):

    #Attempt to clean album
    res = clean_album(user_id, album_id)

    if res == "No files found under user_id and album_id given" :
        return "Could not clean album"
    else:
        album_ref = db.reference(f'users/{user_id}/albums/{album_id}')

        data = album_ref.get()

        if not data:
            return "Album does not exist"

        album_ref.delete()

        return 1
    

'''
This method shows the whole structure for a user, helpful for development
'''

def retrieve_user_structure(user_id):
    # Reference to the specific user's data
    user_ref = db.reference(f'users/{user_id}')
    
    # Get the user's data
    user_data = user_ref.get()
    
    if not user_data:
        return None

    return user_data


'''
These methods are for populating the faces folder for the camera
'''
FACES_FOLDER = 'faces' #path to faces folder

def populate_faces_folder(user_id):
    # Get user data from the database
    user_data = retrieve_user_structure(user_id)  # Modify as needed to get user data
    albums = user_data.get('albums', {})

    # Check if there are any albums to process
    if not albums or all(album is None or not album.get('images', []) for album in albums):
        print("No albums or images found to populate the faces folder.")
        return

    # Iterate over the albums and process images
    for album in albums:
        if album:  # Ensure album is not None
            images = album.get('images', {})
            if not images or all(img_data is None for img_data in images):
                continue  # Skip if no images or only null entries
            
            for img_data in images:
                if img_data:  # Ensure img_data is not None
                    storage_path = img_data.get('storagePath')
                    if storage_path:
                        # Logic to process and populate the faces folder
                        download_image_and_save(storage_path)

def download_image_and_save(storage_path):
    try:
        # Reference to storage bucket
        bucket = storage.bucket()
        
        # Reference to the blob
        blob = bucket.blob(storage_path)
        
        # Check if blob exists
        if not blob.exists():
            print(f"Blob {storage_path} does not exist in storage.")
            return
        
        # Define the local path where the image should be saved
        local_path = os.path.join(FACES_FOLDER, os.path.basename(storage_path))
        
        # Download the blob to a local file
        blob.download_to_filename(local_path)
        print(f"Downloaded {storage_path} to {local_path}")
    
    except Exception as e:
        print(f"Failed to download and save image from {storage_path}: {e}")


