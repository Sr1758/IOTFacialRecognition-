import face_recognition
import pickle
import base64
import numpy as np
import cv2
import os
from database import *

def create_face_encoding_pickle(image, album_name, userID):
    try:
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
        
    except Exception as e:
        print(f"Error in create_face_encoding_pickle: {e}")

def load_face_encodings(userID):
    try:
        f, path = download_pickle(userID)
        known_face_encodings, known_face_names = pickle.load(f)
        f.close()
        # Remove the temporary pickle file
        os.remove(path)
        return known_face_encodings, known_face_names
    except Exception as e:
        print(f"Error in load_face_encodings: {e}")
        return [], []

def save_face_encodings(known_face_encodings, known_face_names, file_path):
    try:
        with open(file_path, 'wb') as f:
            pickle.dump((known_face_encodings, known_face_names), f)
        print(f"Encodings and names saved to {file_path}.")
    except Exception as e:
        print(f"Error in save_face_encodings: {e}")

def remove_user_encodings(album_name, userID):
    try:
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
            pickle.dump((updated_encodings, updated_names), f)
        print(f"Encodings and names saved to {base}.")

        path = f'encodings/{userID}.pkl'

        delete_pickle(path)
        print("Original Pickle Deleted")

        upload_pickle(base, f'encodings/{base}')
        print("New pickle file added to storage")

    except Exception as e:
        print(f"Error in remove_user_encodings: {e}")

def update_face_encodings(image, album_name, userID):
    try:
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
            print("Original Pickle Deleted")

            # Upload encoding to Firebase Storage
            upload_pickle(temp, f'encodings/{temp}')
            
            # Delete the local pickle file
            delete_local_file(temp)
        else:
            print("No face found in the image.")

    except Exception as e:
        print(f"Error in update_face_encodings: {e}")

def recognize_faces(unknown_image, known_face_encodings, known_face_names):
    try:
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
            most_matches_count = match_counts[most_matches_name]
            return most_matches_name, most_matches_count
        
        return "Unknown"
    except Exception as e:
        print(f"Error in recognize_faces: {e}")
        return "Unknown"
