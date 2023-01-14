import cv2
import numpy as np
import math
def nothing(x):
    pass
def get_center(j,dst,a):#逆时针a=0为外圈，为其他为内圈；顺时针反之
    center = 320
    color = dst[j]
    white_count = np.sum(color == 0)
    if white_count <= 10:
        center=320
    else :
      white_index = np.where(color == 0)
      if a==0:
          for i in range(1,white_count):
              if(white_index[0][white_count - i]-white_index[0][white_count - i-1]>=10):#黑像素点连在一起超过10个才会被识别成赛道
                  center = (white_index[0][white_count - 1]+white_index[0][white_count - i])/2
                  break
              else:
                  pass
              center=(white_index[0][white_count - 1]+white_index[0][0])/2
      else:
          for i in range(1, white_count):
              if (white_index[0][i] - white_index[0][i - 1] >= 10):
                center = (white_index[0][0] + white_index[0][i-1])/2
                break
              else:
                  pass
              center=(white_index[0][white_count - 1]+white_index[0][0]) / 2

    direction = center - 320
    a= math.atan2(direction, 480-j)
    direction=a
    #print(direction)
    direction = 57.3 * direction
    #print(direction)
    return direction
# 打开摄像头，图像尺寸640*480（长*高），opencv存储值为480*640（行*列）
cap = cv2.VideoCapture(1)#树莓派上使用改成0，电脑自带一个摄像头故为1
fourcc = cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')
cap.set(cv2.CAP_PROP_FOURCC, fourcc)
WindowName = 'threshold'
cv2.namedWindow(WindowName, cv2.WINDOW_AUTOSIZE)#提供调节二值化阈值的窗口
cv2.createTrackbar('threshold', WindowName, 0, 255, nothing)
while (1):
    angle = 0
    ret, frame = cap.read()
    if ret == False:  # 如果是最后一帧这个值为False
        break
    frame = cv2.GaussianBlur(frame, (3, 3), 0)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # 大津法二值化
    #retval, dst = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU)
    threshold_i = cv2.getTrackbarPos('threshold', WindowName)#窗口调节阈值
    retval, dst = cv2.threshold(gray, threshold_i, 255, cv2.THRESH_BINARY)
    # 膨胀，白区域变大
    dst = cv2.dilate(dst, None, iterations=2)
    # 腐蚀，白区域变小
    dst = cv2.erode(dst, None, iterations=6)
    angle+= get_center(300, dst,0)
    angle+= get_center(320, dst, 0)
    angle+= get_center(340, dst, 0)
    angle+= get_center(360, dst, 0)
    angle+= get_center(380, dst, 0)
    angle+= get_center(400, dst, 0)
    angle=angle/6
    # 计算出center与标准中心点的偏移量
    cv2.imshow("frame", frame)
    cv2.imshow("dst", dst)
    print(angle)
    #print("OTSU：", retval)

    if cv2.waitKey(10) == 27:
      break

# 释放清理
cap.release()
cv2.destroyAllWindows()
