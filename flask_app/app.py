import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask , render_template , jsonify , request
from deep_translator import GoogleTranslator
import cv2
import mediapipe as mp
import numpy as np
import base64
from src.predict import predict_sign
from src.text_builder import TextAnalyzer
from src.translate import translate
import logging


app = Flask(__name__)

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands = 2, min_detection_confidence = 0.5)
text = TextAnalyzer()
last_sign = "" 
translated_str = ""

@app.route("/") #calls index function
def index():
    return render_template("index.html")

@app.route("/languages") #not accepting input
def get_all_supported_languages():
    #key - language name , value - language code
    name_code = GoogleTranslator().get_supported_languages(as_dict = True)
    return jsonify(name_code)

@app.route("/predict", methods = ["POST"]) #acceptiong input- denoted by "methods"
def get_prediction():
    global last_sign
    global translated_str
    data = request.get_json()
    language = data["language"]
    image_data = data["image"] #raw base64 string, something like - data:image/jpeg;base64,/9j/4AAQSkZJRg...
    image_data = image_data.split(",")[1] #things outside , (pure base64 string)
    image_bytes = base64.b64decode(image_data) #b64decode takes the pure base64 string and converts it to raw bytes — the actual binary image data.
    np_array = np.frombuffer(image_bytes, dtype = np.uint8)
    frame = cv2.imdecode(np_array , cv2.IMREAD_COLOR)

    rgb_frame = cv2.cvtColor(frame , cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)
    
    confirmed_sign = ""
    if results.multi_hand_landmarks : 
        dataL = []
        dataR = []
        for i,hand in enumerate(results.multi_hand_landmarks):
            label = results.multi_handedness[i].classification[0].label
            if label.lower() == "left":
                for point in hand.landmark:
                    a = point.x
                    b = point.y
                    c =  point.z
                    dataL.extend([a,b,c])   
            if label.lower() == "right" :
                for point in hand.landmark:
                    a = point.x
                    b = point.y
                    c =  point.z
                    dataR.extend([a,b,c])     
        if dataL == []:
            data = [0] * 63 + dataR 
        elif dataR == []:
            data = dataL + [0] * 63
        else :
            data = dataL + dataR

        if len(data) == 126:
                    prediction = predict_sign(data)
                    prev_len = len(text.sentence)
                    confirmed_sign, _, _  = text.process(prediction)
                    if confirmed_sign is not None:
                        last_sign = confirmed_sign
                    if len(text.sentence) > prev_len:
                        if language != "en":
                            translated_str = translate(" ".join(text.sentence),language)
                        else :
                            translated_str = " ".join(text.sentence) 

    return jsonify({"sign" : last_sign, "word" : "".join(text.word) ,"sentence" : translated_str})

@app.route("/translate", methods = ["POST"])
def translation_when_lang_changed():
    global translated_str
    data = request.get_json()
    language_code = data["code"]

    if text.sentence == []:
        return jsonify("")
    
    if language_code == "en":
        translated_str = " ".join(text.sentence)
        return jsonify(" ".join(text.sentence))
    else :
        translated_str = translate(" ".join(text.sentence),language_code)
        return jsonify(translated_str)



if __name__ == "__main__":
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    app.run(debug = True)
