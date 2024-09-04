import cv2
import face_recognition
import re

def facial_recognition(image_to_check, stored_image):
    try:

        print("image_to_check", image_to_check)
        print("stored_image", stored_image)

        # Check if images are None or empty
        if image_to_check is None or stored_image is None:
            print("One of the images is empty or failed to load.")
            return False
        
        # Convert images to RGB (if needed)
        rgb_image_to_check = cv2.cvtColor(image_to_check, cv2.COLOR_BGR2RGB)
        rgb_stored_image = cv2.cvtColor(stored_image, cv2.COLOR_BGR2RGB)

        # Get the face encodings for the uploaded image and the stored image
        image_to_check_encodings = face_recognition.face_encodings(rgb_image_to_check)
        stored_image_encodings = face_recognition.face_encodings(rgb_stored_image)

        if len(image_to_check_encodings) == 0 or len(stored_image_encodings) == 0:
            print("No faces detected in one of the images.")
            return False

        # Compare the first face encoding in the uploaded image to the first in the stored image
        results = face_recognition.compare_faces([stored_image_encodings[0]], image_to_check_encodings[0])
        
        return results[0]
    
    except cv2.error as cv2_err:
        print(f"OpenCV error in facial_recognition: {cv2_err}")
        return False
    except Exception as e:
        print(f"General error in facial_recognition: {e}")
        return False
    
# Function to extract userID, albumID, and photoID
def extract_ids_from_url(url):
    # Extract the part after "images/"
    filename = url.split('/')[-1].split('?')[0]
    # Remove the ".png" part and split by "-"
    userID, albumID, photoID = filename.replace('.png', '').split('-')
    return userID, albumID, photoID