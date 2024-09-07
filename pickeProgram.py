import face_recognition
import pickle
from database import *

def create_face_encoding_pickle(image, album_name, userID):
    known_face_encodings = []
    known_face_names = []

    # Get face encodings for the image
    face_encodings = face_recognition.face_encodings(image)
    
    # Assume there's only one face per image
    if face_encodings:
        known_face_encodings.append(face_encodings[0])
        known_face_names.append(album_name)

    # Temp is the name of the pickle file which will contain all the encodings and names for a user
    temp = f'{userID}.pkl'

    # Save encodings to a file
    with open(temp, 'wb') as f:
        pickle.dump((known_face_encodings, known_face_names), f)
    
    # Upload encoding to Firebase Storage
    upload_pickle(temp, f'encodings/{temp}')
    
    # Delete the local pickle file
    delete_local_file(temp)

def load_face_encodings(userID):
    f = download_pickle(userID)
    known_face_encodings, known_face_names = pickle.load(f)
    f.close()
    
    return known_face_encodings, known_face_names

def save_face_encodings(known_face_encodings, known_face_names, file_path):
    """
    Save the face encodings and names to a pickle file.

    Args:
        known_face_encodings (list): A list of face encodings.
        known_face_names (list): A list of names corresponding to the face encodings.
        file_path (str): The path where the pickle file will be saved.
    """
    with open(file_path, 'wb') as f:
        pickle.dump((known_face_encodings, known_face_names), f)
    print(f"Encodings and names saved to {file_path}.")

def remove_user_encodings(album_name, userID):
    # Load existing encodings
    known_face_encodings, known_face_names = load_face_encodings(userID)

    # Filter out encodings related to the specified user
    updated_encodings = []
    updated_names = []
    
    for encoding, name in zip(known_face_encodings, known_face_names):
        if name != album_name:
            updated_encodings.append(encoding)
            updated_names.append(name)

    base = f'{userID}.pkl'
    
    # Save the updated encodings back to the pickle file
    with open(base, 'wb') as f:
        pickle.dump((known_face_encodings, known_face_names), f)
    print(f"Encodings and names saved to {base}.")

    path = f'encodings/{userID}.pkl'

    delete_pickle(path)

    print("Original Pickel Deleted")

    upload_pickle(base, f'encodings/{base}')

    print("New pickel file added to storage")

def update_face_encodings(image, album_name, userID):
    # Load existing encodings
    known_face_encodings, known_face_names = load_face_encodings(userID)
    
    # Get encoding
    new_face_encodings = face_recognition.face_encodings(image)
    
    # If face encodings are found, update the pickle file
    if new_face_encodings:
        known_face_encodings.append(new_face_encodings[0])
        known_face_names.append(album_name)

        # Temp is the name of the pickle file which will contain all the encodings and names for a user
        temp = f'{userID}.pkl'

        with open(temp, 'wb') as f:
            pickle.dump((known_face_encodings, known_face_names), f)
        print(f"Updated encoding for {album_name}")

        delete_pickle(f'encodings/{temp}')

        print("Original Pickel Deleted")

        # Upload encoding to Firebase Storage
        upload_pickle(temp, f'encodings/{temp}')
        
        # Delete the local pickle file
        delete_local_file(temp)
    else:
        print("No face found in the image.")

def recognize_faces(unknown_image, known_face_encodings, known_face_names):

    face_encodings = face_recognition.face_encodings(unknown_image)
    
    # Create a dictionary to keep track of matches
    match_counts = {name: 0 for name in set(known_face_names)}

    for face_encoding in face_encodings:
        for known_face_encoding, known_face_name in zip(known_face_encodings, known_face_names):
            if len(known_face_encoding) == 0:
                continue
            
            # Compare the face encoding
            results = face_recognition.compare_faces([known_face_encoding], face_encoding)
            
            if results[0]:
                match_counts[known_face_name] += 1
    
    # Return the name with the most matches
    if match_counts:
        most_matches_name = max(match_counts, key=match_counts.get, default="Unknown")
        return most_matches_name
    
    return "Unknown"