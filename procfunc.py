import os
import matplotlib.pylab as plt
import cv2
import time
import numpy as np
import xml.dom.minidom
import random
from ctypes import *
from sdt_detect import *

imageSize = (360, 640, 3)

##must be called to creat default directory
def setupDir(homeFolder, teamName):
    imgDir = homeFolder + '/images'
    resultDir = homeFolder + '/result'
    timeDir = resultDir + '/time'
    xmlDir = resultDir + '/xml'
    myXmlDir = xmlDir + '/' + teamName
    allTimeFile = timeDir + '/alltime.txt'
    if os.path.isdir(homeFolder):
        pass
    else:
        os.mkdir(homeFolder)
        
    if os.path.isdir(imgDir):
        pass
    else:
        os.mkdir(imgDir)
        
    if os.path.isdir(resultDir):
        pass
    else:
        os.mkdir(resultDir)
        
    if os.path.isdir(timeDir):
        pass
    else:    
        os.mkdir(timeDir)
        
    if os.path.isdir(xmlDir):
        pass
    else:
        os.mkdir(xmlDir)

            
    if os.path.isdir(myXmlDir):
        pass
    else:
        os.mkdir(myXmlDir)
    ##create timefile file
    ftime = open(allTimeFile,'a+')
    ftime.close()

    return [imgDir, resultDir, timeDir, xmlDir, myXmlDir, allTimeFile]

## get image name list
def getImageNames(imgDir):
    nameset1 = []
    nameset2 = []
    namefiles= os.listdir(imgDir)
    for f in namefiles:
        if 'jpg' in f:
            imgname = f.split('.')[0]
            nameset1.append(imgname)
    nameset1.sort(key = int)
    for f in nameset1:
        f = f + ".jpg"
        nameset2.append(f)
    imageNum = len(nameset2)
    return [nameset2, imageNum]

def readImagesBatch(imgDir, allImageName, imageNum, iter, batchNumDiskToDram):
    start = iter*batchNumDiskToDram
    end = start + batchNumDiskToDram
    if end > imageNum:
        end = imageNum
    # batchImageData = np.zeros((end-start, imageSize[0], imageSize[1], imageSize[2]))
    batchImageData = []
    for i in range(start, end):
        imgName = imgDir + '/' + allImageName[i]
        img = cv2.imread(imgName, 1)
        # batchImageData[i-start,:,:] = img[:,:]
        # batchImageData[i-start] = img
        batchImageData.append(img)
        # print batchImageData[i-start]==img
        # exit(1)
        # cv2.imshow("origin", img[:,:])
        # cv2.imshow("origin", batchImageData[i-start])
        # key = cv2.waitKey(200)
        # if key == " ":
        #     cv2.waitKey(0)

    return batchImageData

def det_init():
    detect_init()

def det_cleanup():
    detect_cleanup()

def area(xmin, ymin, xmax, ymax):
    if (xmax < xmin or ymax < ymin):
        return 0
    else:
        return (xmax - xmin) * (ymax - ymin)

## detection and tracking algorithm
def detectionAndTracking(inputImageData, batchNum):
    # print inputImageData.shape
    # exit(1)
    result = np.zeros([batchNum, 4])
    for i in range(batchNum):
        data = inputImageData[i]
        # print data.shape
        # cv2.imshow("origin", data)
        # key = cv2.waitKey(20)
        # if key == " ":
        #     cv2.waitKey(0)

        # res = detect_detect(data.ctypes.data_as(c_void_p), data.shape[0], data.shape[1], -16, -16)
        res = detect_detect(data.ctypes.data_as(c_void_p), data.shape[0], data.shape[1], 0, 0)
        if len(res) == 0:
            result[i, 0] = -1
            result[i, 1] = -1
            result[i, 2] = -1
            result[i, 3] = -1
            continue
        xmin = res[0][1]
        ymin = res[0][2]
        xmax = res[0][3]
        ymax = res[0][4]

        # area_det = area(xmin, ymin, xmax, ymax)
        # x_shift = 1.52545466e-3 * area_det + 7.96178772
        # y_shift = -1.72937148e-3 * area_det + 2.09030376e1
        # x_shift = 1.897e-11*area_det**3+-3.103e-7*area_det**2+1.789e-3*area_det**1+1.835e1
        # y_shift = 9.403e-12*area_det**3+-1.405e-7*area_det**2+7.607e-4*area_det**1+1.805e1
        x_shift = 0
        y_shift = 0

        result[i, 0] = xmin-x_shift
        result[i, 1] = xmax-x_shift
        result[i, 2] = ymin-y_shift
        result[i, 3] = ymax-y_shift

        # cv2.rectangle(inputImageData[i], (int(np.round(float(xmin))), int(np.round(float(ymin)))), (int(np.round(float(xmax))), int(np.round(float(ymax)))), (0, 255, 0))
        # cv2.imshow("detection", inputImageData[i])
        # key = cv2.waitKey(5)
        # if key == 32:           # space
        #     cv2.waitKey(0)
        # elif key == 113:        # q
        #     exit()

    return result

## store the results about detection accuracy to XML files
def storeResultsToXML(resultRectangle, allImageName, myXmlDir):
    for i in range(len(allImageName)):
        doc = xml.dom.minidom.Document()
        root = doc.createElement('annotation')

        doc.appendChild(root)
        nameE = doc.createElement('filename')
        nameT = doc.createTextNode(allImageName[i])
        nameE.appendChild(nameT)
        root.appendChild(nameE)

        sizeE = doc.createElement('size')
        nodeWidth = doc.createElement('width')
        nodeWidth.appendChild(doc.createTextNode("640"))
        nodelength = doc.createElement('length')
        nodelength.appendChild(doc.createTextNode("360"))
        sizeE.appendChild(nodeWidth)
        sizeE.appendChild(nodelength)
        root.appendChild(sizeE)

        object = doc.createElement('object')
        nodeName = doc.createElement('name')
        nodeName.appendChild(doc.createTextNode("NotCare"))
        nodebndbox = doc.createElement('bndbox')
        nodebndbox_xmin = doc.createElement('xmin')
        nodebndbox_xmin.appendChild(doc.createTextNode(str(resultRectangle[i, 0])))
        nodebndbox_xmax = doc.createElement('xmax')
        nodebndbox_xmax.appendChild(doc.createTextNode(str(resultRectangle[i, 1])))
        nodebndbox_ymin = doc.createElement('ymin')
        nodebndbox_ymin.appendChild(doc.createTextNode(str(resultRectangle[i, 2])))
        nodebndbox_ymax = doc.createElement('ymax')
        nodebndbox_ymax.appendChild(doc.createTextNode(str(resultRectangle[i, 3])))
        nodebndbox.appendChild(nodebndbox_xmin)
        nodebndbox.appendChild(nodebndbox_xmax)
        nodebndbox.appendChild(nodebndbox_ymin)
        nodebndbox.appendChild(nodebndbox_ymax)

        #nodebndbox.appendChild(doc.createTextNode("360"))
        object.appendChild(nodeName)
        object.appendChild(nodebndbox)
        root.appendChild(object)

        fileName = allImageName[i].replace('jpg', 'xml')
        fp = open(myXmlDir + "/" + fileName, 'w')
        doc.writexml(fp, indent='\t', addindent='\t', newl='\n', encoding="utf-8")
    return

##write time result to alltime.txt
def write(imageNum,runTime,teamName, allTimeFile):
    FPS = imageNum / runTime
    ftime = open(allTimeFile, 'a+')
    ftime.write( "\n" + teamName + " Frames per second:" + str((FPS)) + ", imgNum: "+ str(imageNum) + ", runtime: " + str(runTime) + '\n')  ## xiaowei xu
    ftime.close()
    return
