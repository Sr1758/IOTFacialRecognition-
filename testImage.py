from database import add_photo, update_enable_notifications, delete_album

from PIL import Image

def create_test_image(file_path):
    img = Image.new('RGB', (100, 100), color = 'red')
    img.save(file_path)

# Create a test image
create_test_image('/tmp/test_image.png')

local_image_path = '/tmp/test_image.png'

userID = 14
albumID = 1

result = add_photo(userID,albumID, local_image_path)

print("result: ")
print(result)