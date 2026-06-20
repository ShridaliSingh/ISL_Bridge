import cv2
import mediapipe as mp
import os
from predict import predict_sign
from text_builder import TextAnalyzer
from speak import speak

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["GLOG_minloglevel"] = "3"

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands = 2, min_detection_confidence = 0.5)

def main():

    text = TextAnalyzer()

    choice = input("""Camera input or Video file ?
                Choose 1 for camera 
                       2 for video file : """).strip()
    while True:

        if choice == "1":
            cap = cv2.VideoCapture(0)
            break

        elif choice == "2":
            video = input("Enter video file path : ").lower().strip()

            while True:
                if not os.path.isfile(video):
                    video = input("Enter correct video file path : ")
                else :
                    break
        
                cap = cv2.VideoCapture(video)
                break

    speech = input("Do you want sentences spoken aloud when you press 'S'? (y/n) ").strip()

    while True:
        if speech == "y" or speech == "n":
            break
        else :
            speech = input("Enter (y/n) : ").strip()

    sentence_str = ""
    while True:  
        success , frame = cap.read()
        if success:
            frame = cv2.flip(frame,1)
            rgb_frame = cv2.cvtColor(frame , cv2.COLOR_BGR2RGB)
            results = hands.process(rgb_frame)

            prediction = "Could not detect"
            confirmed_sign = None
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
                    confirmed_sign, _, _  = text.process(prediction)

            word_str = "".join(text.word)
            sentence_str = " ".join(text.sentence)   

            cv2.putText(frame, f"Sign : {confirmed_sign}", (10,50), cv2.FONT_HERSHEY_SIMPLEX, 1 , (0,255,255), 2)
            cv2.putText(frame, f"Last Word : {word_str}", (10,100), cv2.FONT_HERSHEY_SIMPLEX, 1 , (0,255,255), 2)
            cv2.putText(frame, f"Sentence : {sentence_str}", (10,150), cv2.FONT_HERSHEY_SIMPLEX, 1 , (0,255,255), 2)

            cv2.imshow("Cam",frame)
        elif not success:
            break
        
        #live-cam
        key = cv2.waitKey(1)
        if key == 27:
            cap.release()
            cv2.destroyAllWindows()
            break
        elif key == ord('s'):
            if speech == "y":
                if not sentence_str:
                    pass
                else:
                    speak(sentence_str)

if __name__ == "__main__":
    main()
    





    
        