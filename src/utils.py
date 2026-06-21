from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np

def draw_text(frame, text, position, font_path, size = 32):
    rgb_frame = cv2.cvtColor(frame , cv2.COLOR_BGR2RGB)
    image = Image.fromarray(rgb_frame)

    obj = ImageDraw.Draw(image)
    font = ImageFont.truetype(font_path,size)
    obj.text(position, text, font=font, fill = (255,255,0))

    bgr_frame = cv2.cvtColor(np.array(image) , cv2.COLOR_RGB2BGR)
    
    return bgr_frame



