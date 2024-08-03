import firebase_admin
from firebase_admin import db, credentials, storage

#authenticate to firebase
cred = credentials.Certificate("credentials.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://ios-alzheimers-app-default-rtdb.firebaseio.com/',
    'storageBucket': 'gs://ios-alzheimers-app.appspot.com'
})

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
def add_photo(user_id, album_id, local_image_path, storage_image_path):

    # Reference to storage
    bucket = storage.bucket()

    #Need to determine number of images already within an account
    album_ref = db.reference(f'users/{user_id}/albums/{album_id}')
    data = album_ref.get()
    
    if 'numImages' not in data:
        print("There is no num images field in this album")
        return 0
    elif data['numImages'] >= 20:
        print("Number of images exceeds limit for individual album")
        return 0
    else:
        numImages = data['numImages']
    
    img_id = numImages + 1
    
    img_prefix = f"{user_id}-{album_id}-{img_id}"

    # Upload
    blob = bucket.blob(storage_image_path)
    blob.upload_from_filename(local_image_path)

    return 1

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
    sorting_by_name = f'{user_id}-{album_id}'

    # Lists location of all images that correspond to the a particular album
    blobs = bucket.list_blobs(prefix=sorting_by_name)

    #If no images found under user and album specified to check
    if not blobs:   
        return "No files found under user_id and album_id given"
    
    # Delete every image that corresponds to that user and album
    for blob in blobs:
        blob.delete()

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

    if res == "No files found under user_id and album_id given" :
        return "Could not clean album"
    else:
        album_ref = db.reference(f'users/{user_id}/albums/{album_id}')

        data = album_ref.get()

        if not data:
            return "Album does not exist"

        album_ref.delete()

        return 1








    