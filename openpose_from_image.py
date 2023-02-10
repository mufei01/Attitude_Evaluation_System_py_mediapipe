import sys
import cv2
import os
from sys import platform

# Import Openpose (Windows/Ubuntu/OSX)
dir_path = os.path.dirname(os.path.realpath(__file__))
try:
    # Windows Import
    if platform == "win32":
        # 如果在visual studio上编译的时候使用的是Release模式，把Debug换成Release
        os.environ['PATH'] = os.environ['PATH'] + ';' + dir_path + './Debug;' + dir_path + './bin;'
        import pyopenpose as op
    else:
        # Change these variables to point to the correct folder (Release/x64 etc.)
        sys.path.append('../../python')
        from openpose import pyopenpose as op
except ImportError as e:
    print(
        'Error: OpenPose library could not be found. Did you enable `BUILD_PYTHON` in CMake and have this Python script in the right folder?')
    raise e


def startOpenpose(pictureFile):
    # 设置Openpose模型并初始化
    params = dict()
    params["model_folder"] = "./models/"
    opWrapper, datum = op.WrapperPython(), op.Datum()
    opWrapper.configure(params)
    opWrapper.start()

    datum = op.Datum()
    # 读取图片
    imageToProcess = cv2.imread(r'%s' % pictureFile[0])
    datum.cvInputData = imageToProcess
    opWrapper.emplaceAndPop(op.VectorDatum([datum]))

    # Display Image
    print("Body keypoints: \n" + str(datum.poseKeypoints))
    # cv2.imshow("OpenPose 1.7.0 - Tutorial Python API", datum.cvOutputData)
    cv2.waitKey(0)
    return imageToProcess, datum.cvOutputData


if __name__ == "__main__":
    pass
'''输出数据对照
{0,  "Nose"},
{1,  "Neck"},
{2,  "RShoulder"},
{3,  "RElbow"},
{4,  "RWrist"},
{5,  "LShoulder"},
{6,  "LElbow"},
{7,  "LWrist"},
{8,  "MidHip"},
{9,  "RHip"},
{10, "RKnee"},
{11, "RAnkle"},
{12, "LHip"},
{13, "LKnee"},
{14, "LAnkle"},
{15, "REye"},
{16, "LEye"},
{17, "REar"},
{18, "LEar"},
{19, "LBigToe"},
{20, "LSmallToe"},
{21, "LHeel"},
{22, "RBigToe"},
{23, "RSmallToe"},
{24, "RHeel"},
{25, "Background"}
————————————————
版权声明：本文为CSDN博主「AIHGF」的原创文章，遵循CC 4.0 BY-SA版权协议，转载请附上原文出处链接及本声明。
原文链接：https://blog.csdn.net/zziahgf/article/details/
'''