import cv2
import face_recognition
import re

def facial_recognition(image_to_check, stored_image):
    try:
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
    
    except Exception as e:
        print(f"Error in facial_recognition: {e}")
        return False
    
def extract_album_id(url):
    # This regex matches the userID, albumID, and imgNumber in the format userID-albumID-imgNumber.png
    pattern = r'/(\d+)-(\d+)-(\d+)\.png'
    match = re.search(pattern, url)

    if match:
        user_id, album_id, img_number = match.groups()
        return album_id
    else:
        return None