from PIL import Image
import os

def crop(input_image, tile_width, tile_height, rotation=0):
    image = Image.open(input_image)
    image_width, image_height = image.size
    k = 0
    
    for x in range(image_width // tile_width):
        for y in range(image_height // tile_height):
            box = (y * tile_width, x * tile_height, (y+1) * tile_width, (x+1) * tile_height)
            tile = image.crop(box).rotate(rotation)
            directory_path = os.path.join("tmp", "images")
            if not os.path.exists(directory_path):
                os.mkdir(directory_path)
            k += 1
            path = os.path.join(directory_path, f"Img-{k}.jpg")
            tile.save(path)

input_image = "tmp/logos_original.jpg"
height = 75
width = 100
rotation = 0
hard_mode = True

if hard_mode:
    rotation = 180


# Enumerate with yield, paste cropped image in new image
# for index, tile in enumerate(crop(input_image, width, height, rotation)):
#     img = Image.new("RGB", (width, height), 255)
#     img.paste(tile)