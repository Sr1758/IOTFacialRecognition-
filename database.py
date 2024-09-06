import firebase_admin
from firebase_admin import db, credentials, storage
import os

#authenticate to firebase
cred = credentials.Certificate("credentials.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://ios-alzheimers-app-default-rtdb.firebaseio.com/',
    'storageBucket': 'ios-alzheimers-app.appspot.com'
})

'''
Uses realtime database to store account data.
user_id: identifies each user (the userID key found on the mysql database)
user_info: json file that contains fields for a user entity

user_info:{
    "userID": INT
    "enableNotifications": BOOL
    "numAlbums": INT
    "modelNumber": VARCHAR(12)
}
'''
def create_user_account(user_id, user_info):
    ref = db.reference('users')
    user_ref = ref.child(user_id)
    user_ref.set(user_info)
    return 1

#Update user account to have a given model number
def updateCamera(user_id, modelNumber):
    ref = db.reference('users')
    user_ref = ref.child(user_id)
    user_ref.update({'modelNumber': modelNumber})
    return 1

# Retrieves the model number for every user on the realtime database
def retrieve_all_model_numbers():
    ref = db.reference('users')
    users = ref.get()

    if not users:
        print("No users found.")
        return []

    # Initialize an empty list to collect model numbers
    modelNumbers = []
    user_ids = []

    # Iterate over the users data and collect model numbers and user IDs
    for user_id, user_data in users.items():
        if 'modelNumber' in user_data:
            modelNumbers.append(user_data['modelNumber'])
            user_ids.append(user_id)

    model_number_collection = {
        'userID': user_ids,
        'modelNumbers': modelNumbers
    }

    return model_number_collection

# Validate whether model number exists for a given user
def validate_model_number(user_id, model_number):
    # Reference to the specific user's data
    user_ref = db.reference(f'users/{user_id}')

    # Get the user's current data
    user_data = user_ref.get()

    # Check whether the user exists
    if not user_data:
        return "User does not exist"

    # Retrieve all model numbers and their associated account IDs
    models_data = retrieve_all_model_numbers()

    # Extract necessary data from json packet
    users = models_data['userID']
    models = models_data['modelNumbers']

    # Check if the model number is used by another user
    if model_number in models:
        index_1 = users.index(user_id) if user_id in users else -1
        index_2 = models.index(model_number)

        if models.count(model_number) == 1 and index_1 != index_2:
            return "Another user already has this model number"

    return 1


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

    # Reference to the specific user's data
    albums_ref = db.reference(f'users/{user_id}/albums')
    albums_data = albums_ref.get()

    if not albums_data:
        return 0
    
    # Check if albums_data is a list and filter out None values
    if isinstance(albums_data, list):
        albums_data = [album for album in albums_data if album is not None]

    # Initialize an empty list to collect album IDs and names

    names = []
    albumID = []
    
    # Iterate over the albums data and collect album IDs and names

    for  item in albums_data:
        names.append(item['name'])
        albumID.append(item['albumID'])
    
    '''
    print("albumID: ", albumID)
    print("Names: ", names)
    '''

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
def add_photo(user_id, album_id, local_image_path):
    try:
        # Reference to storage
        bucket = storage.bucket()

        # Check if the bucket was obtained correctly
        if not bucket:
            print("Error: Could not obtain bucket reference")
            return 0

        # Determine number of images already within an account
        album_ref = db.reference(f'users/{user_id}/albums/{album_id}')
        data = album_ref.get()
        
        if not data:
            print("Album data not found.")
            return 0

        if 'numImages' not in data:
            print("There is no numImages field in this album")
            return 0
        elif data['numImages'] >= 20:
            print("Number of images exceeds limit for individual album")
            return 0
        else:
            numImages = data['numImages']
        
        img_id = numImages + 1
        img_prefix = f"{user_id}-{album_id}-{img_id}"
        storage_image_path = f"images/{img_prefix}.png"  # Ensure path format

        # Upload
        if not os.path.exists(local_image_path):
            print(f"Local image path does not exist: {local_image_path}")
            return 0

        blob = bucket.blob(storage_image_path)
        blob.upload_from_filename(local_image_path)

        # Update the number of images
        album_ref.update({'numImages': img_id})

        print(f"Successfully uploaded {local_image_path} to {storage_image_path}")

        return 1

    except Exception as e:
        print(f"Error in add_photo: {e}")
        return 0

'''
Clean out all the images within an album.
'''
def clean_album(user_id, album_id):

    path = 'images/'

    # Reference to storage
    bucket = storage.bucket()

    '''
    Character array used to sort the image list for the images that correspond 
    to a particular user's album.
    '''
    sorting_by_name = f'images/{user_id}-{album_id}'

    # Lists location of all images that correspond to the a particular album
    blobs = bucket.list_blobs(prefix=sorting_by_name)
    
    # Track whether any blobs were found and deleted
    deleted_any = False

    # Delete every image that corresponds to that user and album
    for blob in blobs:
        deleted_any = True
        blob.delete()

    # If no images were found under the user and album specified
    if not deleted_any:
        return "No files found under user_id and album_id given"
    
    album_ref = db.reference(f'users/{user_id}/albums/{album_id}')

    album_ref.update({
        'numImages': 0
    })

    return 1

'''
Delete album images and album entity in realtime database
'''
def delete_album(user_id, album_id):

    #Attempt to clean album
    res = clean_album(user_id, album_id)

    album_ref = db.reference(f'users/{user_id}/albums/{album_id}')

    data = album_ref.get()

    if not data:
        return "Album does not exist"

    album_ref.delete()

    return 1


#Retrieve url of all photos for a particular user
def retrieve_all_user_photos(user_id):
    try:
        # Reference to the user's albums in the Realtime Database
        albums_ref = db.reference(f'users/{user_id}/albums')
        albums_data = albums_ref.get()

        if not albums_data:
            print("No albums found for this user.")
            return []
        
        #print('albums:', albums_data)

        # Initialize an empty list to collect all image URLs
        all_image_urls = []
        bucket = storage.bucket()

        # Check if albums_data is a list
        if isinstance(albums_data, list):
            albums_data = {str(index): album for index, album in enumerate(albums_data) if album}

        # Iterate over each album
        for album_id, album_info in albums_data.items():
            # Check if the album contains images
            if 'numImages' in album_info and album_info['numImages'] > 0:
                num_images = album_info['numImages']

                # Collect URLs for each image in the album
                for img_num in range(1, num_images + 1):
                    img_prefix = f"{user_id}-{album_id}-{img_num}"
                    storage_image_path = f"images/{img_prefix}.png"

                    # Retrieve the image URL from Firebase Storage
                    blob = bucket.blob(storage_image_path)
                    image_url = blob.generate_signed_url(version="v4", expiration=3600)  # URL valid for 1 hour
                    all_image_urls.append(image_url)

        return all_image_urls

    except Exception as e:
        print(f"Error in retrieve_all_user_photos: {e}")
        return []

def download_image(image_path):
    try:
        # Reference to Firebase Storage
        bucket = storage.bucket()

        # Create a blob object for the image
        blob = bucket.blob(image_path)

        # Local path where the file will be saved
        storage_path = "downloaded_image.png"

        # Download the image data as bytes
        image_data = blob.download_as_bytes()

        print(f"File downloaded successfully.")
        
        return image_data
    
    except Exception as e:
        print(f"Error in download_image: {e}")
        return None

def retrieve_user_id_by_model_number(model_number):
    try:
        # Reference to the users collection in the Realtime Database
        ref = db.reference('users')
        users = ref.get()

        if not users:
            #print("No users found.")
            return None

        # Iterate over the users data and check for the matching model number
        for user_id, user_data in users.items():
            if 'modelNumber' in user_data and user_data['modelNumber'] == model_number:
                #print(f"User with model number {model_number} found: User ID is {user_id}")
                return user_id

        #print(f"No user found with model number {model_number}")
        return None

    except Exception as e:
        print(f"Error in retrieve_user_id_by_model_number: {e}")
        return None

def get_enable_notifications(user_id):
    user_ref = db.reference(f'users/{user_id}')
    
    # Retrieve the user data
    user_data = user_ref.get()

    if not user_data:
        return "User does not exist"

    # Retrieve the enableNotifications value
    if 'enableNotifications' in user_data:
        return user_data['enableNotifications']
    else:
        return "Notification setting not found"

def get_album_data(user_id, album_id):
    album_ref = db.reference(f'users/{user_id}/albums/{album_id}')
    
    # Retrieve the album data
    album_data = album_ref.get()

    if not album_data:
        return "Album does not exist"
    
    return album_data



    







    