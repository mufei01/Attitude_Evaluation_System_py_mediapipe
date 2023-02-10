import cv2
import mediapipe as mp
import time

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_holistic = mp.solutions.holistic

pTime = 0
cap = cv2.VideoCapture(0)
# cap = cv2.VideoCapture("./3.mp4")
with mp_holistic.Holistic(
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as holistic:
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            # 加载一个视频的话，把continue换成break
            continue
            # break
        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # BGR图转RGB
        results = holistic.process(image)  # 处理三通道彩色图
        # 画图
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)  # RGB转BGR
        mp_drawing.draw_landmarks(
            image,
            results.face_landmarks,#画脸
            mp_holistic.FACEMESH_CONTOURS,
            landmark_drawing_spec=None,
            connection_drawing_spec=mp_drawing_styles
            .get_default_face_mesh_contours_style())
        mp_drawing.draw_landmarks(
            image,
            results.pose_landmarks,  # 画人体骨架
            mp_holistic.POSE_CONNECTIONS,
            landmark_drawing_spec=mp_drawing_styles
            .get_default_pose_landmarks_style())
        # 画左右手
        mp_drawing.draw_landmarks(image, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS)
        mp_drawing.draw_landmarks(image, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS)

        # 右手21个节点坐标
        if results.right_hand_landmarks:
            for index, landmarks in enumerate(results.right_hand_landmarks.landmark):
                print(index, landmarks)
        # 鼻子坐标
        # print(results.pose_landmarks.landmark[mp_holistic.PoseLandmark.NOSE])

        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime
        # 图片 添加的文字 位置 字体 字体大小 字体颜色 字体粗细
        cv2.putText(image, str(int(fps)), (70, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)

        cv2.imshow('MediaPipe Holistic',
                   cv2.flip(image, 1)  # 镜像画面
                   # image
                   )
        if cv2.waitKey(5) & 0xFF == 27:
            break
cap.release()
