from time import sleep
import cv2 as cv
import csv
import copy
from picamera2 import Picamera2
import mediapipe as mp

from keypoint_classifier.keypoint_classifier import KeyPointClassifier 
from diod_control import Diodes
from servocontrol import ServoControl
import I2C_LCD_driver


# Inicjalizacja kompnentów
picam2 = Picamera2()
picam2.start()
mylcd = I2C_LCD_driver.lcd()
diod = Diodes()
servo = ServoControl()


# Główna pętla programu
def main():
    # Zmienne pomocnicze
    prev = 0
    prevServo = 0

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

    #Rysowanie schematu dłoni
    mp_draw = mp.solutions.drawing_utils

    while True:
        # Wychodzenie z programu za pomocą q
        key = cv.waitKey(10)
        if key & 0xFF == ord('q'):
            mylcd.lcd_clear()
            servo.delete()
            sleep(1)
            break

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

                # Obliczanie pozycji landmarków
                landmark_list = create_landmark_list_in_pixels(debug_frame, hand_landmarks)

                # Normalizacja pozycji landmarków
                normalised_landmark_list = normalise_landmark(landmark_list)

                # Klasyfikacja gestów jako identyfikatorów gestów
                hand_sign_id = keypoint_classifier(normalised_landmark_list)
                
                # Wykonywanie akcji związanych z gestami
                if (hand_sign_id != prev):
                    prev = hand_sign_id
                    # Jeżeli wykryta ręka jest lewa
                    if left_or_right == "Left":
                        if (hand_sign_id == 2):
                            mylcd.lcd_clear()
                            mylcd.lcd_display_string("Serwo", 1)
                            mylcd.lcd_display_string("Lewo", 2)
                            if(prevServo == -1):
                                servo.rotateMiddle()
                                prevServo = 0
                                sleep(1)
                            else:
                                servo.rotateRight()
                                prevServo = 1
                                sleep(1)
                            print(keypoint_classifier_labels[2])

                    # Jeżeli wykryta ręka jest prawa
                    if left_or_right == "Right":
                        
                        match hand_sign_id:
                            case 1:
                                mylcd.lcd_clear()
                                mylcd.lcd_display_string("Serwo", 1)
                                mylcd.lcd_display_string("Prawo", 2)
                                if(prevServo == 1):
                                    servo.rotateMiddle()
                                    prevServo = 0
                                    sleep(1)
                                else:
                                    servo.rotateLeft()
                                    prevServo = -1
                                    sleep(1)
                                print(keypoint_classifier_labels[1])
                            case 3:
                                diod_control(keypoint_classifier_labels, 3, True, True, False)
                            case 4:
                                diod_control(keypoint_classifier_labels, 4, False, True, False)
                            case 5:
                                diod_control(keypoint_classifier_labels, 5, False, False, True)
                            case 6:
                                diod_control(keypoint_classifier_labels, 6, True, False, False)             
                            case 7:
                                diod_control(keypoint_classifier_labels, 7, False, False, False)              
                            case 8:
                                diod_control(keypoint_classifier_labels, 8, True, True, True)             
                            case 9:
                                diod_control(keypoint_classifier_labels, 9, True, False, True)
                            case 0:
                                diod_control(keypoint_classifier_labels, 0, False, True, True)
                        
        # Wyświetlenie klatki  
        cv.imshow("Wykrywanie gestow", frame)
        
    # Zamknięcie kamery i zamknięcie okien
    picam2.close()
    cv.destroyAllWindows()


# Funkcja kontrolująca diody wraz z ekranem
def diod_control(classifier, nr, red, yellow, blue):
    diod.turnOn(red=red, yellow=yellow, blue=blue)
    print(classifier[nr])
    mylcd.lcd_clear()
    mylcd.lcd_display_string("Diody", 1)
    mylcd.lcd_display_string(classifier[nr], 2)


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


# Funkcja zmieniająca elementy listy jako wynik funkcji na poszczególnych elementach listy
def list_mapping_from_function(function, list):
    temp_list = []
    for elem in list:
        temp_list.append(function(elem))
    return temp_list


# Wpisywanie zebranych danych do pliku 
def logging_csv(num, mode, landmark_list):
    if mode == 1 and (0 <= num <= 9):
        csv_path = 'keypoint_classifier/keypoint.csv'

        model_file = open(csv_path, 'a', newline="")
        writer = csv.writer(model_file)
        writer.writerow([num, *landmark_list])
        model_file.close()
    return


# Transformacja pozycji landmarków do postaci ułatwiającej analizę
def normalise_landmark(landmark_list):
    temp_landmark_list = transform_landmark_positions(landmark_list)

    temp_landmark_list = lower_dimension(temp_landmark_list)

    max_value = max(list_mapping_from_function(abs, temp_landmark_list))

    temp_landmark_list = list_mapping_from_function(lambda n: n / max_value, temp_landmark_list)

    return temp_landmark_list


if __name__ == '__main__':
    main()