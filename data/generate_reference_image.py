from skimage.data import astronaut
from skimage.io import imsave


def write_reference_image():
    path = 'reference_image.png'
    im = astronaut()
    imsave(path, im)


if __name__ == '__main__':
    write_reference_image()
