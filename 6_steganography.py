import os
from PIL import Image 
from itertools import chain, cycle


dir_name = os.path.dirname(__file__)


# convert string message to binary string
def str_to_binstr(message): 
    return ''.join(format(ord(char), '08b') for char in message)


# convert binary string to string message
def binstr_to_str(binstr):
    if int(binstr, 2) % 8 != 0:
        binstr += '0' * (8 - int(binstr, 2) % 8)
    return ''.join(chr(int(binstr[i:i+8], 2)) for i in range(0, len(binstr) - 8, 8))


# open image in current directory
def open_image(file_name):
    file_path =  dir_name + '/' + file_name
    return Image.open(file_path, 'r')


# calculate pixel brightness
def brightness(rgb):
    return 0.298 * rgb[0] + 0.586 * rgb[1] + 0.114 * rgb[2]


# modify pixel (blue colour)
def modified_pixel(pixel, bit, coords, L=1.0):
    blue = pixel[2]
    
    b = brightness(pixel)
    if b == 0:
        b = 5 / L
        
    if bit == '1':
        blue += L * b
        if blue > 255:
            blue = 255
    else:
        blue -= L * b
        if blue < 0:
            blue = 0
    blue = int(round(blue, 0))
        
    return (pixel[0], pixel[1], blue)
        

# check that coordinates are within limits
def in_bounds(coords, w, h):
    x = coords[0]
    y = coords[1]
    return x >= 0 and x < w and y >= 0 and y < h 
        

# get coordinate in ranges
# (x - sigma, y)-(x + sigma, y), (x, y - sigma)-(x, y + sigma)
def get_coords(coords, sigma, w, h):
    x = coords[0]
    y = coords[1]
    return filter(lambda coords: in_bounds(coords, w, h),
                   chain(
                        zip(range(x - sigma, x), cycle([y])),
                        zip(range(x + 1, x + sigma + 1), cycle([y])),
                        zip(cycle([x]), range(y - sigma, y)),
                        zip(cycle([x]), range(y + 1, y + sigma + 1))
                        ))
        

# encode message in image
def kjb_encode(image, message):
    w = image.size[0]
    # h = image.size[1]
    # (x0, y0) = (w // 3, h // 3)
    (x0, y0) = (0, 0)
    (x, y) = (x0, y0)
    binstr = str_to_binstr(message)
    pixels = image.load()
    
    for bit in binstr:
        mod_pix = modified_pixel(pixels[x, y], bit, (x, y))
        print("{} {}-{}".format(x+y, pixels[x, y], mod_pix))
        pixels[x, y] = mod_pix
        if x == w - 1:
            x = 0
            y += 1
        else:
            x += 1
    
    return (x0, y0), (x, y)


# decode message from image
def kjb_decode(image, coords, sigma=3):
    binstr = ''
    pixels = image.load()
    
    x1, y1 = coords[0]
    x2, y2 = coords[1]
    
    for x in range(x1, x2 + 1):
        for y in range(y1, y2 + 1):
            pix = pixels[x, y]
            
            coords = get_coords((x, y), sigma, image.size[0], image.size[1])
            b = [brightness(pixels[c]) for c in coords]
            b_mean = sum(b) / len(b)
            
            blue = pix[2]
            if blue < b_mean:
                binstr += '0'
            else:
                binstr += '1'
                
            print('{} ({} < {}) ? {}'.format(x+y, blue, b_mean, blue < b_mean))
    
    print('binstr: {}'.format(binstr))
    return binstr_to_str(binstr)


# main function
def main():
    message = 'I am a teapot'
    # image_name = 'batman.jpg'
    image_name = input('Enter image file name: ')
    enc_image_name = 'enc_' + image_name
    
    print('========ENCODE========')
    print('Message: {}'.format(message))
    print('Source image: {}'.format(image_name))
    
    # encode and save a new image
    image = open_image(image_name)
    enc_image = image.copy()
    image.close()
    
    coords = kjb_encode(enc_image, message)
    print('Pixel coordinates: {}'.format(coords))
    
    enc_image.save(enc_image_name)
    print('SUCCESS')
    
    print('========DECODE========')
    print('Encoded image: {}'.format(enc_image_name))
    
    # decode encrypted message
    dec_message = kjb_decode(enc_image, coords)
    enc_image.close()
    print('Decoded message: {}'.format(dec_message))
    
    accuracy = sum(ch[0] == ch[1] for ch in zip(message, dec_message)) / len(message)
    print('Accuracy: {}'.format(accuracy))
    
    print('SUCCESS')


# calling the main function
if __name__ == '__main__':
    main()
    