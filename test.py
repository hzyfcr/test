import serial
import cv2
import numpy as np
import math
import time


def nothing(x):
    pass


def get_center(j, dst, a):
    center = 320
    color = dst[j, 40:600]
    # if a==0:
    white_count = np.sum(color == 0)
    # else :
    #   white_count = np.sum(color == 255)
    if white_count <= 10:
        center = 320
    else:
        white_index = np.where(color == 0)
        if a == 0:
            for i in range(1, white_count):
                if (white_index[0][white_count - i] - white_index[0][white_count - i - 1] >= 10):
                    center = (white_index[0][white_count - 1] + white_index[0][white_count - i]) / 2
                    break
                else:
                    pass
                center = (white_index[0][white_count - 1] + white_index[0][0]) / 2
        else:
            for i in range(1, white_count):
                if (white_index[0][i] - white_index[0][i - 1] >= 3):
                    center = (white_index[0][0] + white_index[0][i - 1]) / 2
                    break
                else:
                    pass
                center = (white_index[0][white_count - 1] + white_index[0][0]) / 2

    direction = center - 320
    # a= math.atan2(direction, 480-j)
    # direction=a
    # print(direction)
    # direction = 57.3 * direction
    # print(direction)
    return direction


def find_state(dst, hang, color):
    if color == 0:  # 黑线
        a = dst[hang, 40:600]
        count = np.sum(a == 0)
        # print(count)
        ############以下为预设90和腐蚀下的估计阈值
        if count >= 140:  # 像素点大于160，到达停止点，出现大量干扰，驶出赛道等；
            b = dst[hang - 30, 40:600]
            c = dst[hang + 30, 40:600]
            count1 = np.sum(b == 0)
            count2 = np.sum(c == 0)
            if (count1 <= 25 and count2 > 25):
                state = 2
                return state
            elif (count2 <= 25 and count1 > 25):
                state = 0
                # print("c")
                return state
            else:
                state = 1
                return state

        if (count < 140 and count > 0):  # 说明处于双赛道，有字母出现，或者扫描到了少量杂点，后续再做区分；
            # print("normal")
            state = 0
            return state
        else:
            state = 0
            return state


# 打开摄像头，图像尺寸640*480（长*高），opencv存储值为480*640（行*列）
cap = cv2.VideoCapture(0)
fourcc = cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')
cap.set(cv2.CAP_PROP_FOURCC, fourcc)

# WindowName = 'threshold'
# cv2.namedWindow(WindowName, cv2.WINDOW_AUTOSIZE)
# cv2.createTrackbar('threshold', WindowName, 0, 255, nothing)
ser = serial.Serial("/dev/ttyS0", 115200)
while (1):
    t1 = time.time()
    angle = 0
    ret, frame = cap.read()
    # 转化为灰度图
    if ret == False:  # 如果是最后一帧这个值为False
        break
    # frame = cv2.GaussianBlur(frame, (3, 3), 0)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # 大津法二值化
    # retval, dst = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU)
    # threshold_i = cv2.getTrackbarPos('threshold', WindowName)
    retval, dst = cv2.threshold(gray, 110, 255, cv2.THRESH_BINARY)
    # 膨胀，白区域变大
    dst = cv2.dilate(dst, None, iterations=2)
    # 腐蚀，白区域变小
    dst = cv2.erode(dst, None, iterations=2)
    judge = find_state(dst, 350, 0)
    angle += get_center(240, dst, 0)
    angle += get_center(270, dst, 0)
    angle += get_center(300, dst, 0)
    angle += get_center(330, dst, 0)
    angle += get_center(360, dst, 0)
    angle += get_center(390, dst, 0)
    angle = angle / 6
    # cv2.line(dst,(0,235),(640,235),(0,0,0),2)
    # cv2.line(dst,(37,0),(37,480),(255,255,255),2)
    # cv2.line(dst,(603,0),(603,480),(255,255,255),2)
    # cv2.line(frame,(0,350),(640,350),(0,0,0),2)
    # cv2.line(frame,(0,320),(640,320),(0,0,0),2)
    # cv2.line(frame,(0,380),(640,380),(0,0,0),2)
    # cv2.imshow("frame", frame)
    # cv2.imshow("dst", dst)
    # print(angle)

    angle_str = str(round(angle, 3)) + "00000";
    angle_arr = list(angle_str[0:6])
    for i in range(len(angle_arr)):
        ser.write(bytes(angle_arr[i], encoding='utf-8'))
    if judge == 0:
        pass
    elif judge == 1:
        ser.write(bytes("sastop", encoding='utf-8'))
        print("time to sastop")
    elif judge == 2:
        ser.write(bytes("scstop", encoding='utf-8'))
        # print("time to scstop")
    t2 = time.time()
    t3 = t2 - t1
    print(int(1 / t3))
    if cv2.waitKey(10) == 27:
        break

# 释放清理
cap.release()
cv2.destroyAllWindows()
