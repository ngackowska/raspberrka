from time import sleep
import cv2 as cv
import csv
import copy
import numpy as np
from picamera2 import Picamera2
import mediapipe as mp

from keypoint_classifier.keypoint_classifier import KeyPointClassifier 
from diod_control import Diodes
from servocontrol import ServoControl


picam2 = Picamera2()
picam2.start()

diod = Diodes()
# servo = ServoControl()


def main():
    prev = 0
    prev_count = 0
    prevs = []

    # Ładownie modelu

    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=2,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.5,
    )

    keypoint_classifier = KeyPointClassifier()


    # Czytanie etykiet keypointów 

    label_file = open('keypoint_classifier/keypoint_classifier_label.csv',encoding='utf-8-sig')
    keypoint_classifier_labels_raw = csv.reader(label_file)
    keypoint_classifier_labels = []
    for row in keypoint_classifier_labels_raw:
        keypoint_classifier_labels.append(row[0])
    label_file.close()

    mode = 0


    mp_draw = mp.solutions.drawing_utils



    while True:
        # Wychodzenie z programu za pomocą q
        key = cv.waitKey(10)
        if key & 0xFF == ord('q'):
            # servo.delete()
            sleep(1)
            break

        # Ustalanie trybu (uczenie / czytanie gestów)
        num, mode = mode_selection(key, mode)

        # Przechwytywanie obrazu
        frame = picam2.capture_array()
        
        frame = cv.flip(frame, 0)
        debug_frame = copy.deepcopy(frame)

        # Detekcja ruchów

        frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)

        frame.flags.writeable = False
        results = hands.process(frame)
        frame.flags.writeable = True


        if results.multi_hand_landmarks is not None:
            for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                # Etykieta czy wykryta raka jest lewa czy prawa
                left_or_right = handedness.classification[0].label

                # Obliczanie wymiarów obramówki ręki
                border = calc_border(debug_frame, hand_landmarks)

                # Obliczanie pozycji landmarków
                landmark_list = create_landmark_list_in_pixels(debug_frame, hand_landmarks)

                # Normalizacja pozycji landmarków
                normalised_landmark_list = normalise_landmark(landmark_list)

                # Wpisaywanie pozycji landmarków do pliku z nauczonymi gestami
                logging_csv(num, mode, normalised_landmark_list)

                # Klasyfikacja gestów jako identyfikatorów gestów
                hand_sign_id = keypoint_classifier(normalised_landmark_list)

                # Jeżeli wykryta ręka jest lewa
                if left_or_right == "Left":
                    if (hand_sign_id == 1):
                        diod.turnOn(red=True, yellow=False, blue=False)
                        # servo.rotateRight()
                        print("left")

                    #tu wykrywanie gestow sterujących

                # Jeżeli wykryta ręka jest prawa
                if left_or_right == "Right":
                    
                    prev = left_or_right
                    if (hand_sign_id == 2):
                        diod.turnOn(red=False, yellow=True, blue=False)
                        # servo.rotateLeft()
                        print("right")
                        
                    


                    #tu wykrywanie gestow alfabetu

        #Rysowanie obramówki  i informacji o wykrytym geście
                debug_frame = draw_border(debug_frame, border)
                debug_frame = draw_info_text(
                    debug_frame,
                    border,
                    handedness,
                    keypoint_classifier_labels[hand_sign_id],
                )
        
        # Wykonanie rysowania 
        debug_frame = draw_info(debug_frame, mode, num)

        # Wyświetlenie ramki  
        cv.imshow("Wykrywanie gestow", frame)
        
    # Zamknięcie kamery i zamknięcie okien
    picam2.close()
    cv.destroyAllWindows()

    



# Funkcja określająca tryb programu na podstawie informacji wpisanych z klawiatury
def mode_selection(key, mode):
    num = -1
    if 48 <= key <= 57:  # 0 ~ 9
        num = key - 48
    if key == 110:  # n
        mode = 0
    if key == 107:  # k
        mode = 1
    if key == 104:  # h
        mode = 2
    return num, mode


# Funkcja wyliczająca pozycje landmarków w pikselach na podstawie obrazu
def create_landmark_list_in_pixels(frame, landmarks):
    frame_width = frame.shape[1]
    frame_height = frame.shape[0]

    landmark_points = []

    for landmark in landmarks.landmark:
        landmark_x = min(int(landmark.x * frame_width), frame_width - 1)
        landmark_y = min(int(landmark.y * frame_height), frame_height - 1)
        landmark_points.append([landmark_x, landmark_y])

    return landmark_points


# Funckja transformująca koordynaty landmarków na relatywne w obrębie obramówki ręki
def transform_landmark_positions(landmark_list):
    temp_landmark_list = copy.deepcopy(landmark_list)

    base_x, base_y = 0, 0
    i = 0
    for landmark_point in temp_landmark_list:
        if i == 0:
            base_x, base_y = landmark_point[0], landmark_point[1]

        temp_landmark_list[i][0] = temp_landmark_list[i][0] - base_x
        temp_landmark_list[i][1] = temp_landmark_list[i][1] - base_y
        i += 1

    return temp_landmark_list


# Funkcja łącząca listę dwuwymiarową do listy jednowymiarowej
def lower_dimension(landmark_list):
    temp_landmark_list = []
    for list in landmark_list:
        for item in list:
            temp_landmark_list.append(item)
    return temp_landmark_list


# Funkcja zmieniająca elementy listy jako wynik funkcji na poszczególnych 
# elementach listy
def list_mapping_from_function(function, list):
    temp_list = []
    for elem in list:
        temp_list.append(function(elem))
    return temp_list


# Transformacja pozycji landmarków do postaci ułatwiającej analizę
def normalise_landmark(landmark_list):
    temp_landmark_list = transform_landmark_positions(landmark_list)

    temp_landmark_list = lower_dimension(temp_landmark_list)

    max_value = max(list_mapping_from_function(abs, temp_landmark_list))

    temp_landmark_list = list_mapping_from_function(lambda n: n / max_value, temp_landmark_list)

    return temp_landmark_list


# Wpisywanie zebranych danych do pliku 
def logging_csv(num, mode, landmark_list):
    if mode == 1 and (0 <= num <= 9):
        csv_path = 'keypoint_classifier/keypoint.csv'

        model_file = open(csv_path, 'a', newline="")
        writer = csv.writer(model_file)
        writer.writerow([num, *landmark_list])
        model_file.close()

    return


# Funkcja obliczająca wymiary obramówki
def calc_border(frame, landmarks):
    frame_width = frame.shape[1]
    frame_height = frame.shape[0]

    landmark_array = np.empty((0, 2), int)

    for landmark in landmarks.landmark:
        landmark_x = min(int(landmark.x * frame_width), frame_width - 1)
        landmark_y = min(int(landmark.y * frame_height), frame_height - 1)

        landmark_point = [np.array((landmark_x, landmark_y))]

        landmark_array = np.append(landmark_array, landmark_point, axis=0)

    x, y, w, h = cv.boundingRect(landmark_array)
    x_w = x + w
    y_h = y + h

    return [x, y, x_w, y_h]


# Funkcja dodająca obramówke do obrazu
def draw_border(frame, border):
    cv.rectangle(frame, (border[0], border[1]), (border[2], border[3]), (0, 0, 0), 1)

    return frame


def draw_info_text(frame, border, handedness, hand_sign_text):
    cv.rectangle(frame, (border[0], border[1]), (border[2], border[1] - 22), (0, 0, 0), -1)

    info_text = handedness.classification[0].label[0:]
    if hand_sign_text != "":
        info_text = info_text + ':' + hand_sign_text

    cv.putText(frame, info_text, (border[0] + 5, border[1] - 4), cv.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv.LINE_AA)

    return frame


def draw_info(frame, mode, num):
    mode_string = ['Logging Key Point', 'Logging Point History']
    if 1 <= mode <= 2:
        cv.putText(frame, "MODE:" + mode_string[mode - 1], (10, 90), cv.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv.LINE_AA)
        if 0 <= num <= 9:
            cv.putText(frame, "NUM:" + str(num), (10, 110), cv.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv.LINE_AA)
    return frame


if __name__ == '__main__':
    main()







