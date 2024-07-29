import firebase_admin
from firebase_admin import db, credentials 

#authenticate to firebase
cred = credentials.Certificate("credentials.json")
firebase_admin.initialize_app(cred, {"databaseURL": ""})

def create_album(user_id, name, bio):

    # Reference to the user's albums collection
    user_ref = db.collection('users').document(user_id)
    albums_ref = user_ref.collection('albums')

    # Count the number of existing albums
    album_count = len(list(albums_ref.stream()))

    if album_count >= 10:
        return {'error': 'User already has 10 albums. Cannot add more.'}

    album_ref = user_ref.collection('albums').document()
    album_ref.set({
        'albumID': album_ref.id,
        'name': name,
        'bio': bio
    })
    return album_ref.id

def get_albums(user_id):
    user_ref = db.collection('users').document(user_id)
    albums_ref = user_ref.collection('albums')
    albums = albums_ref.stream()

    # Collect all albums into a list
    album_list = []
    for album in albums:
        album_data = album.to_dict()
        album_list.append(album_data)

    return album_list

def delete_album(user_id, album_id):
    # Reference to the user's document
    user_ref = db.collection('users').document(user_id)
    user_doc = user_ref.get()

    if not user_doc.exists:
        return {'error': 'User not found'}

    # Reference to the specific album
    album_ref = user_ref.collection('albums').document(album_id)
    album_doc = album_ref.get()

    if not album_doc.exists:
        return {'error': 'Album not found'}

    # Delete the album
    album_ref.delete()
    return {'message': f'Album {album_id} deleted successfully'}






    