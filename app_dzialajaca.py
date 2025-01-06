import csv
import copy
import itertools

from time import sleep

from picamera2 import Picamera2

import cv2 as cv
import numpy as np
import mediapipe as mp

from keypoint_classifier.keypoint_classifier import KeyPointClassifier 

from diod_control import Diodes


picam2 = Picamera2()
picam2.start()

diod = Diodes()


def main(): 
    prev = 0
    prev_count = 0
    prevs = []

    word_save = False

    word = ""

    #do wyswietlania recta
    use_brect = True


    # Model load #############################################################
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=2,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.5,
    )

    keypoint_classifier = KeyPointClassifier()

    # labels ###########################################################
    label_file = open('keypoint_classifier/keypoint_classifier_label.csv',encoding='utf-8-sig')
    keypoint_classifier_labels_raw = csv.reader(label_file)
    keypoint_classifier_labels = []
    for row in keypoint_classifier_labels_raw:
        keypoint_classifier_labels.append(row[0])
    label_file.close()

    # Coordinate history #################################################################

    #  ########################################################################
    mode = 0

    heil_mode = False

    while True:
        # Process Key (ESC: end) #################################################
        key = cv.waitKey(10)
        if key == 27:  # ESC
            break
        number, mode = select_mode(key, mode)

        # Camera capture #####################################################
        image = picam2.capture_array()
        image = cv.flip(image, 1)  # Mirror display
        debug_image = copy.deepcopy(image)

        # Detection implementation #############################################################
        image = cv.cvtColor(image, cv.COLOR_BGR2RGB)

        image.flags.writeable = False
        results = hands.process(image)
        image.flags.writeable = True

        #  ####################################################################
        if results.multi_hand_landmarks is not None:
            for hand_landmarks, handedness in zip(results.multi_hand_landmarks,
                                                  results.multi_handedness):

                # left or right hand
                hand_label = handedness.classification[0].label

                # Bounding box calculation
                brect = calc_bounding_rect(debug_image, hand_landmarks)
                # Landmark calculation
                landmark_list = calc_landmark_list(debug_image, hand_landmarks)

                # Conversion to relative coordinates / normalized coordinates
                pre_processed_landmark_list = pre_process_landmark(
                    landmark_list)

                # Write to the dataset file
                logging_csv(number, mode, pre_processed_landmark_list)

                # Hand sign classification
                hand_sign_id = keypoint_classifier(pre_processed_landmark_list)


                if hand_label == "Left":
                    if hand_sign_id == 3:
                        word_save = True
                    elif hand_sign_id == 0:
                        word = ""

                if hand_label == "Left" and hand_sign_id ==7:
                    heil_mode = True

                if hand_label == "Right":

                    if (prev == 3 and hand_sign_id != 3) or prev_count != 0:
                        prev_count += 1
                        prevs.append(hand_sign_id)

                        if prev_count == 5:

                            if hand_sign_id == 6 and heil_mode:
                                heil_mode = False
                                from diod_control import Diodes


                            # q.put(keypoint_classifier_labels[prevs[-1]])    # tu można dac którego jest najwięcej
                            if word_save:
                                word += " " + keypoint_classifier_labels[prevs[-1]]
                            prev_count = 0
                            prevs = []

                    if (hand_sign_id == 8):
                        
                        diod.turnOn(red=True, yellow=True, blue=True)
                        sleep(1)
                        diod.turnOn(red=False, yellow=False, blue=False)


                    prev = hand_sign_id
                
                # Drawing part
                #print(keypoint_classifier_labels[hand_sign_id])
                debug_image = draw_bounding_rect(use_brect, debug_image, brect)
                debug_image = draw_info_text(
                    debug_image,
                    brect,
                    handedness,
                    keypoint_classifier_labels[hand_sign_id],
                )

        debug_image = draw_info(debug_image, mode, number)

        # Screen reflection #############################################################
        cv.imshow('Hand Gesture Recognition', debug_image)

    picam2.close()
    cv.destroyAllWindows()


def select_mode(key, mode):
    number = -1
    if 48 <= key <= 57:  # 0 ~ 9
        number = key - 48
    if key == 110:  # n
        mode = 0
    if key == 107:  # k
        mode = 1
    if key == 104:  # h
        mode = 2
    return number, mode



def calc_landmark_list(frame, landmarks):
    frame_width, frame_height = frame.shape[1], frame.shape[0]

    landmark_points = []

    # Keypoint
    for landmark in landmarks.landmark:
        landmark_x = min(int(landmark.x * frame_width), frame_width - 1)
        landmark_y = min(int(landmark.y * frame_height), frame_height - 1)
        landmark_points.append([landmark_x, landmark_y])

    return landmark_points

# def pre_process_landmark(landmark_list):
#     temp_landmark_list = copy.deepcopy(landmark_list)

#     # Convert to relative coordinates
#     base_x, base_y = 0, 0
#     for index, landmark_point in enumerate(temp_landmark_list):
#         if index == 0:
#             base_x, base_y = landmark_point[0], landmark_point[1]

#         temp_landmark_list[index][0] = temp_landmark_list[index][0] - base_x
#         temp_landmark_list[index][1] = temp_landmark_list[index][1] - base_y

#     # Convert to a one-dimensional list
#     temp_landmark_list = list(
#         itertools.chain.from_iterable(temp_landmark_list))

#     # Normalization
#     max_value = max(list(map(abs, temp_landmark_list)))

#     def normalize_(n):
#         return n / max_value

#     temp_landmark_list = list(map(normalize_, temp_landmark_list))

#     return temp_landmark_list


def transform_landmark_positions(landmark_list):
    temp_landmark_list = copy.deepcopy(landmark_list)

    # Convert to relative coordinates
    base_x, base_y = 0, 0
    i = 0
    for landmark_point in temp_landmark_list:
        if i == 0:
            base_x, base_y = landmark_point[0], landmark_point[1]

        temp_landmark_list[i][0] = temp_landmark_list[i][0] - base_x
        temp_landmark_list[i][1] = temp_landmark_list[i][1] - base_y
        i += 1

    return temp_landmark_list



def lower_dimension(landmark_list):
    temp_landmark_list = []
    for list in landmark_list:
        for item in list:
            temp_landmark_list.append(item)
    return temp_landmark_list


def list_mapping_from_function(function, list):
    temp_list = []
    for elem in list:
        temp_list.append(function(elem))
    return temp_list



def pre_process_landmark(landmark_list):
    temp_landmark_list = transform_landmark_positions(landmark_list)

    temp_landmark_list = lower_dimension(temp_landmark_list)

    max_value = max(list_mapping_from_function(abs, temp_landmark_list))

    temp_landmark_list = list_mapping_from_function(lambda n: n / max_value, temp_landmark_list)

    return temp_landmark_list


def logging_csv(number, mode, landmark_list):
    if mode == 1 and (0 <= number <= 9):
        csv_path = 'model/keypoint_classifier/keypoint.csv'

        model_file = open(csv_path, 'a', newline="")
        writer = csv.writer(model_file)
        writer.writerow([number, *landmark_list])
        model_file.close()

    return


def draw_bounding_rect(use_brect, image, brect):
    if use_brect:
        # Outer rectangle
        cv.rectangle(image, (brect[0], brect[1]), (brect[2], brect[3]),
                     (0, 0, 0), 1)

    return image


def calc_bounding_rect(image, landmarks):
    image_width, image_height = image.shape[1], image.shape[0]

    landmark_array = np.empty((0, 2), int)

    for landmark in landmarks.landmark:
        landmark_x = min(int(landmark.x * image_width), image_width - 1)
        landmark_y = min(int(landmark.y * image_height), image_height - 1)

        landmark_point = [np.array((landmark_x, landmark_y))]

        landmark_array = np.append(landmark_array, landmark_point, axis=0)

    x, y, w, h = cv.boundingRect(landmark_array)

    return [x, y, x + w, y + h]



def draw_info_text(image, brect, handedness, hand_sign_text):
    cv.rectangle(image, (brect[0], brect[1]), (brect[2], brect[1] - 22),
                 (0, 0, 0), -1)

    info_text = handedness.classification[0].label[0:]
    if hand_sign_text != "":
        info_text = info_text + ':' + hand_sign_text
    cv.putText(image, info_text, (brect[0] + 5, brect[1] - 4),
               cv.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv.LINE_AA)

    return image


def draw_info(image, mode, number):
    mode_string = ['Logging Key Point', 'Logging Point History']
    if 1 <= mode <= 2:
        cv.putText(image, "MODE:" + mode_string[mode - 1], (10, 90),
                   cv.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1,
                   cv.LINE_AA)
        if 0 <= number <= 9:
            cv.putText(image, "NUM:" + str(number), (10, 110),
                       cv.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1,
                       cv.LINE_AA)
    return image


if __name__ == '__main__':
    main()
