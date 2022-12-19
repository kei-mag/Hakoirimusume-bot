from imgurpython import ImgurClient
from picamera import PiCamera

client_id = '<IMGUR CLIENT ID VALUE>'
client_secret = '<IMGUR CLIENT SECRET VALUE>'

camera = PiCamera()
camera.resolution = (1920, 1080)

camera.capture ('captured.jpg')

client = ImgurClient(client_id, client_secret)

image = client.upload_from_path('./captured.jpg', config=None, anon=True)

print(image["link"])
