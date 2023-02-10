import cv2
import mediapipe as mp
import numpy as np


def calculate_angle(a, b, c):
    a = np.array(a)  # First
    b = np.array(b)  # Mid
    c = np.array(c)  # End

    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)

    if angle > 180.0:
        angle = 360 - angle

    return angle


mp_drawing = mp.solutions.drawing_utils  # 画图
mp_holistic = mp.solutions.holistic  # 全身肢体
mp_drawing_styles = mp.solutions.drawing_styles


def startOpenpose(pictureFile):
    with mp_holistic.Holistic(static_image_mode=True,  # 选择静态图片还是连续视频帧
                              model_complexity=2,  # 选择人体姿态关键点检测模型，0性能差但快，2性能好但慢，1介于之间
                              smooth_landmarks=True,  # 是否选择平滑关键点
                              min_detection_confidence=0.5,  # 置信度阈值
                              min_tracking_confidence=0.5) as holistic:  # 追踪阈值
        image = cv2.imread(r'%s' % pictureFile[0])  # 读取图片
        # image_height, image_width, _ = image.shape  # 获取坐标
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # 颜色通道转换
        results = holistic.process(image)

        annotated_image = image.copy()  # 复制图片

        # 计算角度

        landmarks = results.pose_landmarks.landmark

        right_shoulder = [landmarks[mp_holistic.PoseLandmark.RIGHT_SHOULDER.value].x,
                          landmarks[mp_holistic.PoseLandmark.RIGHT_SHOULDER.value].y]
        right_elbow = [landmarks[mp_holistic.PoseLandmark.RIGHT_ELBOW.value].x,
                       landmarks[mp_holistic.PoseLandmark.RIGHT_ELBOW.value].y]
        right_wrist = [landmarks[mp_holistic.PoseLandmark.RIGHT_WRIST.value].x,
                       landmarks[mp_holistic.PoseLandmark.RIGHT_WRIST.value].y]
        left_shoulder = [landmarks[mp_holistic.PoseLandmark.LEFT_SHOULDER.value].x,
                         landmarks[mp_holistic.PoseLandmark.LEFT_SHOULDER.value].y]
        left_elbow = [landmarks[mp_holistic.PoseLandmark.LEFT_ELBOW.value].x,
                      landmarks[mp_holistic.PoseLandmark.LEFT_ELBOW.value].y]
        left_wrist = [landmarks[mp_holistic.PoseLandmark.LEFT_WRIST.value].x,
                      landmarks[mp_holistic.PoseLandmark.LEFT_WRIST.value].y]
        right_hip = [landmarks[mp_holistic.PoseLandmark.RIGHT_HIP.value].x,
                     landmarks[mp_holistic.PoseLandmark.RIGHT_HIP.value].y]
        right_knee = [landmarks[mp_holistic.PoseLandmark.RIGHT_KNEE.value].x,
                      landmarks[mp_holistic.PoseLandmark.RIGHT_KNEE.value].y]
        right_ankle = [landmarks[mp_holistic.PoseLandmark.RIGHT_ANKLE.value].x,
                       landmarks[mp_holistic.PoseLandmark.RIGHT_ANKLE.value].y]
        left_hip = [landmarks[mp_holistic.PoseLandmark.LEFT_HIP.value].x,
                    landmarks[mp_holistic.PoseLandmark.LEFT_HIP.value].y]
        left_knee = [landmarks[mp_holistic.PoseLandmark.LEFT_KNEE.value].x,
                     landmarks[mp_holistic.PoseLandmark.LEFT_KNEE.value].y]
        left_ankle = [landmarks[mp_holistic.PoseLandmark.LEFT_ANKLE.value].x,
                      landmarks[mp_holistic.PoseLandmark.LEFT_ANKLE.value].y]

        angle14 = calculate_angle(right_shoulder, right_elbow, right_wrist)  # 右手臂，右手肘的角度 14
        angle13 = calculate_angle(left_shoulder, left_elbow, left_wrist)  # 左手臂，左手肘的角度 13
        angle26 = calculate_angle(right_hip, right_knee, right_ankle)  # 右大腿，右小腿的角度 26
        angle25 = calculate_angle(left_hip, left_knee, left_ankle)  # 左大腿，左小腿的角度 25
        angle24 = calculate_angle(right_shoulder, right_hip, right_knee)  # 右肩，右大腿的角度 24
        angle23 = calculate_angle(left_shoulder, left_hip, left_knee)  # 左肩，左大腿的角度 23
        angle12 = calculate_angle(right_elbow, right_shoulder, right_hip)  # 右大臂，右臀的角度 12
        angle11 = calculate_angle(left_elbow, left_shoulder, left_hip)  # 左大臂，左臀的角度 11
        actions = np.array([angle14, angle13, angle26, angle25, angle24, angle23, angle12, angle11])
        print(actions)

        # 图片上显示角度
        # cv2.putText(annotated_image, str(round(angle14)),
        #             tuple(np.multiply(right_elbow, [640, 480]).astype(int)),
        #             cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA
        #             )
        #
        # cv2.putText(annotated_image, str(round(angle13)),
        #             tuple(np.multiply(left_elbow, [640, 480]).astype(int)),
        #             cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA
        #             )
        #
        # cv2.putText(annotated_image, str(round(angle26)),
        #             tuple(np.multiply(right_knee, [640, 480]).astype(int)),
        #             cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA
        #             )
        #
        # cv2.putText(annotated_image, str(round(angle25)),
        #             tuple(np.multiply(left_knee, [640, 480]).astype(int)),
        #             cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA
        #             )
        #
        # cv2.putText(annotated_image, str(round(angle24)),
        #             tuple(np.multiply(right_hip, [640, 480]).astype(int)),
        #             cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA
        #             )
        #
        # cv2.putText(annotated_image, str(round(angle23)),
        #             tuple(np.multiply(left_hip, [640, 480]).astype(int)),
        #             cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA
        #             )
        #
        # cv2.putText(annotated_image, str(round(angle12)),
        #             tuple(np.multiply(right_shoulder, [640, 480]).astype(int)),
        #             cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA
        #             )
        #
        # cv2.putText(annotated_image, str(round(angle11)),
        #             tuple(np.multiply(left_shoulder, [640, 480]).astype(int)),
        #             cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA
        #             )

        # if results.pose_landmarks:
        # print(
        #     f'Nose coordinates: ('
        #     f'{results.pose_landmarks.landmark[mp_holistic.PoseLandmark.NOSE].x * image_width}, '
        #     f'{results.pose_landmarks.landmark[mp_holistic.PoseLandmark.NOSE].y * image_height})'
        # )

        # mp_drawing.draw_landmarks(
        #     annotated_image, results.face_landmarks, mp_holistic.FACE_CONNECTIONS)  # 脸
        # mp_drawing.draw_landmarks(
        #     annotated_image, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS)  # 左手
        # mp_drawing.draw_landmarks(
        #     annotated_image, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS)  # 右手
        mp_drawing.draw_landmarks(
            annotated_image, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS,
            landmark_drawing_spec=mp_drawing_styles
            .get_default_pose_landmarks_style())  # 肢体

        # cv2.imshow('annotated_image',annotated_image)
        # cv2.imwrite('2.png', annotated_image)

        # cv2.waitKey(0)
        # holistic.close()
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)  # 颜色通道转换
        annotated_image = cv2.cvtColor(annotated_image, cv2.COLOR_RGB2BGR)  # 颜色通道转换
        return image, annotated_image, actions
