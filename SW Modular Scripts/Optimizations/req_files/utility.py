import cv2
import numpy as np
import math


def RetLargestContour(gray):
    LargestContour_Found = False
    thresh=np.zeros(gray.shape,dtype=gray.dtype)
    _,bin_img = cv2.threshold(gray,0,255,cv2.THRESH_BINARY)
    #Find the two Contours for which you want to find the min distance between them.
    cnts = cv2.findContours(bin_img, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)[1]
    Max_Cntr_area = 0
    Max_Cntr_idx= -1
    for index, cnt in enumerate(cnts):
        area = cv2.contourArea(cnt)
        if area > Max_Cntr_area:
            Max_Cntr_area = area
            Max_Cntr_idx = index
            LargestContour_Found = True
    if (Max_Cntr_idx!=-1):
        thresh = cv2.drawContours(thresh, cnts, Max_Cntr_idx, (255,255,255), -1) # [ contour = less then minarea contour, contourIDx, Colour , Thickness ]
    return thresh, LargestContour_Found

def Distance_(a,b):
    return math.sqrt( ( (a[1]-b[1])**2 ) + ( (a[0]-b[0])**2 ) )

def ApproxDistBWCntrs(cnt,cnt_cmp):
    # compute the center of the contour
    M = cv2.moments(cnt)
    cX = int(M["m10"] / M["m00"])
    cY = int(M["m01"] / M["m00"])
    # compute the center of the contour
    M_cmp = cv2.moments(cnt_cmp)
    cX_cmp = int(M_cmp["m10"] / M_cmp["m00"])
    cY_cmp = int(M_cmp["m01"] / M_cmp["m00"])
    minDist=Distance_((cX,cY),(cX_cmp,cY_cmp))
    Centroid_a=(cX,cY)
    Centroid_b=(cX_cmp,cY_cmp)
    return minDist,Centroid_a,Centroid_b


def Estimate_MidLane(BW,MaxDistance):
    #cv2.namedWindow("BW_zero",cv2.WINDOW_NORMAL)
    BW_zero= cv2.cvtColor(BW,cv2.COLOR_GRAY2BGR)
    #Find the two Contours for which you want to find the min distance between them.
    cnts= cv2.findContours(BW, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)[1]#3ms
    MinArea=1
    cnts_Legit=[]
    for index, _ in enumerate(cnts):
        area = cv2.contourArea(cnts[index])
        if area > MinArea:
            cnts_Legit.append(cnts[index])
    cnts=cnts_Legit
    # Cycle through each point in the Two contours & find the distance between them.
    # Take the minimum Distance by comparing all other distances & Mark that Points.
    CntIdx_BstMatch = []# [BstMatchwithCnt0,BstMatchwithCnt1,....]
    Closests_Pixels_list = []
    #200msec
    for index, cnt in enumerate(cnts):
        prevmin_dist = 100000
        Bstindex_cmp = 0
        #BstClosests_Pixels =0 
        BstCentroid_a=0      
        BstCentroid_b=0      
        for index_cmp in range(len(cnts)-index):
            index_cmp = index_cmp + index
            cnt_cmp = cnts[index_cmp]
            if (index!=index_cmp):
                min_dist,Centroid_a,Centroid_b  = ApproxDistBWCntrs(cnt,cnt_cmp)

                #Closests_Pixels=(cnt[min_dstPix_Idx[0]],cnt_cmp[min_dstPix_Idx[1]])
                if(min_dist < prevmin_dist):
                    if (len(CntIdx_BstMatch)==0):
                        prevmin_dist = min_dist
                        Bstindex_cmp = index_cmp
                        #BstClosests_Pixels = Closests_Pixels
                        BstCentroid_a=Centroid_a
                        BstCentroid_b=Centroid_b   

                    else:
                        Present= False
                        for i in range(len(CntIdx_BstMatch)):
                            if ( (index_cmp == i) and (index == CntIdx_BstMatch[i]) ):
                                Present= True
                        if not Present:
                            prevmin_dist = min_dist
                            Bstindex_cmp = index_cmp
                            #BstClosests_Pixels = Closests_Pixels
                            BstCentroid_a=Centroid_a
                            BstCentroid_b=Centroid_b   
        if ((prevmin_dist!=100000 ) and (prevmin_dist>MaxDistance)):
            break
        if (type(BstCentroid_a)!=int):
            CntIdx_BstMatch.append(Bstindex_cmp)
            #Closests_Pixels_list.append(BstClosests_Pixels)
            #cv2.line(BW_zero,(BstClosests_Pixels[0][0][0],BstClosests_Pixels[0][0][1]),(BstClosests_Pixels[1][0][0],BstClosests_Pixels[1][0][1]),(0,0,255),thickness=2)
            cv2.line(BW_zero,BstCentroid_a,BstCentroid_b,(0,255,0),thickness=2)
            #cv2.imshow("BW_zero",BW_zero)
    
    #cv2.imwrite("D:/Had_LuQ/MidlaneClosestJoined.png",BW_zero)
    BW_zero = cv2.cvtColor(BW_zero,cv2.COLOR_BGR2GRAY)

    BW_Largest,Largest_found = RetLargestContour(BW_zero)#3msec

    if(Largest_found):
        return BW_Largest
    else:
        return BW