import mediapipe as mp
import cv2

# Video camera input
cap = cv2.VideoCapture(0)
# Width and height of window
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# mediapipe drawing solution
mp_drawing = mp.solutions.drawing_utils
# mediapipe hand solution
mp_hand = mp.solutions.hands
hand = mp_hand.Hands()

while True:
    success, frame = cap.read()
    if success:
        RGB_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hand.process(RGB_frame)
        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hand.HAND_CONNECTIONS)
                print(hand_landmarks)
        cv2.imshow("capture image", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cv2.destroyAllWindows()
cap.release()
