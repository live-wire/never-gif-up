import cv2
from PIL import Image
import imageio
import datetime
import numpy as np
import sys

import logging
logging.disable(logging.WARNING)


# Click on Spacebar to capture images and Escape when you're done!
def show_webcam(mirror=False, outfile = "webcam.gif"):
    cam = cv2.VideoCapture(0)
    lst = []
    print("Original FPS", cam.get(cv2.CAP_PROP_FPS))
    while True:
        ret_val, img = cam.read()
        if mirror: 
            img = cv2.flip(img, 1)
        cv2.imshow('my webcam', img)
        temp = cv2.waitKey(1)
        if temp == 32:
            imgPIL = Image.fromarray(img)
            lst.append(img)
            # img.save("latest.jpeg")

        if temp == 27:
            break  # esc to quit
    cv2.destroyAllWindows()
    create_gif(lst, outfile=outfile)

def prepareImage(inputf, newshape = (128, 128)):
    if type(inputf) is np.ndarray or type(inputf) is imageio.core.util.Array:
        testImg = inputf
    else:
        print(type(inputf))
        testImg = np.asarray(Image.open(inputf))
    # Converting the image to black and white
    if len(testImg.shape) >= 3:
        testImg = np.mean(testImg,axis=2)
    testImg.astype(np.uint8)
    resized_image = cv2.resize(testImg, newshape)
    # Instead of checking the size of the JPEG image, let's check the size of storing the image as a numpy-2D-array
    resized_image = np.reshape(resized_image.flatten().tolist(), resized_image.shape)
    return resized_image

def create_gif(images, duration=1, outfile = 'webcam.gif', already_prepared=False):
    preparedImages = images
    if not already_prepared:
        preparedImages = list(map(prepareImage, images))
    imageio.mimsave(outfile, preparedImages, duration=duration)

def split_gif(giffile= 'webcam.gif'):
    images = imageio.mimread(giffile)
    return list(map(prepareImage, images))

def main():
    if len(sys.argv) > 1:
        show_webcam(mirror=True, outfile = sys.argv[1])
    else:
        show_webcam(mirror=True)

if __name__ == '__main__':
    main()