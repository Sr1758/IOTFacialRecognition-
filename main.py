import face_recognition  # Import the face_recognition library for face detection and recognition
import os  # Import the os module for interacting with the operating system
import cv2  # Import the OpenCV library for image and video processing
import numpy as np  # Import NumPy for numerical operations
import math  # Import the math library for mathematical functions
import sys  # Import the sys module to exit the program

# Function to load an image in RGB format
def load_image_rgb(image_path):
    image = cv2.imread(image_path)  # Read the image from the specified path
    if image is None:
        raise ValueError(f"Unable to load image '{image_path}'")  # Raise an error if the image cannot be loaded
    if image.dtype != np.uint8:
        raise ValueError(f"Image '{image_path}' is not 8-bit")
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # Convert the image from BGR to RGB format

# Function to calculate the confidence of a face match
def face_confidence(face_distance, face_match_threshold=0.6):
    range_val = (1.0 - face_match_threshold)  # Calculate the range value based on the threshold
    linear_val = (1.0 - face_distance) / (range_val * 2.0)  # Calculate the linear value for confidence

    if face_distance > face_match_threshold:
        return str(round(linear_val * 100, 2)) + '%'  # Return the confidence if the distance is above the threshold
    else:
        value = (linear_val * ((1.0 - linear_val) * math.pow((linear_val - 0.5) * 2, 0.2))) * 100
        return str(round(value, 2)) + '%'  # Return the confidence if the distance is below the threshold

# Class for face recognition
class FaceRecognition:
    def __init__(self):
        self.known_face_encodings = []  # List to store known face encodings
        self.known_face_names = []  # List to store names of known faces
        self.encode_faces()  # Encode faces on initialization

    # Method to encode faces from the 'faces' directory
    def encode_faces(self):

        faces_dir = 'faces1'  # Directory containing the known faces
        if not os.path.exists(faces_dir):
            raise FileNotFoundError(f"Directory '{faces_dir}' not found. Please create the directory and add face images.")
        
        for image in os.listdir(faces_dir):  # Loop through all files in the 'faces' directory
            image_path = os.path.join(faces_dir, image)  # Get the full path of the image
            if not image.lower().endswith(('.png', '.jpg', '.jpeg')):  # Skip non-image files
                continue
            try:
                print(f'Loading image: {image_path}')
                face_image = load_image_rgb(image_path)  # Load the image in RGB format
                
                #Test start 
                if face_image.dtype != np.uint8:
                    print(f"Image '{image_path}' is not 8-bit. Found dtype: {image.dtype}")
                    
                # Check if the image is in RGB format (OpenCV reads images in BGR format)
                if len(face_image.shape) == 3 and face_image.shape[2] == 3:
                    print(f"Image '{image_path}' is 8-bit and RGB (BGR in OpenCV).")
                elif len(face_image.shape) == 2:
                    print(f"Image '{image_path}' is 8-bit and grayscale.")
                else:
                    print(f"Image '{image_path}' has an unsupported format. Shape: {image.shape}")
                #Test end

                face_encodings = face_recognition.face_encodings(face_image)

                print("Stop1")

                if len(face_encodings) == 0:
                    print(f"No face found in image {image_path}")
                    continue
                
                print("Stop 2")

                face_encoding = face_encodings[0]  # Get the face encoding

                print("Stop 3")

                self.known_face_encodings.append(face_encoding)  # Append the face encoding to the list
                self.known_face_names.append(image)  # Append the image name to the list
            except Exception as e:
                print(f'Error loading image {image_path}: {e}')  # Print an error message if image loading fails

        print(self.known_face_names)  # Print the names of the known faces

    # Method to run face recognition
    def run_recognition(self):
        video_capture = cv2.VideoCapture(0)  # Open the default camera

        if not video_capture.isOpened():
            sys.exit('Video source not found...')  # Exit if the camera is not found

        while True:
            ret, frame = video_capture.read()  # Capture a frame from the video source

            if not ret:
                print("Failed to retrieve frame from video source")
                break  # Break the loop if the frame cannot be retrieved

            try:
                small_frame = cv2.resize(frame, (0,0), fx=0.25, fy=0.25)  # Resize the frame for faster processing
                rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)  # Convert the frame to RGB format

                face_locations = face_recognition.face_locations(rgb_small_frame)  # Find face locations in the frame
                face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)  # Get face encodings

                face_names = []  # List to store names of detected faces
                for face_encoding in face_encodings:
                    matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)  # Compare faces
                    name = 'Unknown'  # Default name is 'Unknown'
                    confidence = 'Unknown'  # Default confidence is 'Unknown'

                    if len(self.known_face_encodings) > 0:
                        face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)  # Get face distances
                        best_match_index = np.argmin(face_distances)  # Get the index of the best match

                        if matches[best_match_index]:
                            name = self.known_face_names[best_match_index]  # Get the name of the best match
                            confidence = face_confidence(face_distances[best_match_index])  # Get the confidence of the best match

                    face_names.append(f'{name} ({confidence})')  # Append the name and confidence to the list

                for (top, right, bottom, left), name in zip(face_locations, face_names):
                    top *= 4
                    right *= 4
                    bottom *= 4
                    left *= 4  # Scale back up face locations since the frame was resized

                    cv2.rectangle(frame, (left, top), (right, bottom), (0,0,255), 2)  # Draw a box around the face
                    cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0,0,255), -1)  # Draw a label box
                    cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)  # Draw a label with a name

            except Exception as e:
                print(f'Error processing frame: {e}')  # Print an error message if frame processing fails

            cv2.imshow('Face Recognition', frame)  # Display the resulting frame
            if cv2.waitKey(1) == ord('q'):
                break  # Exit the loop when 'q' is pressed

        video_capture.release()  # Release the capture
        cv2.destroyAllWindows()  # Close all OpenCV windows

# Main function to run face recognition
if __name__ == '__main__':
    fr = FaceRecognition()  # Create a FaceRecognition object
    fr.run_recognition()  # Run face recognition


