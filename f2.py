import numpy as np
import cv2
from matplotlib import pyplot as plt

MIN_MATCH_COUNT = 10

img1 = cv2.imread('model7.png',0)          # queryImage
#img2 = cv2.imread('main.jpg',0) # trainImage

# Initiate SIFT detector

sift = cv2.xfeatures2d.SIFT_create()
# find the keypoints and descriptors with SIFT
cap = cv2.VideoCapture(0)
FLANN_INDEX_KDTREE = 0
index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
search_params = dict(checks = 50)
kp1, des1 = sift.detectAndCompute(img1,None)
h,w = img1.shape
pts = np.float32([ [0,0],[0,h-1],[w-1,h-1],[w-1,0] ]).reshape(-1,1,2)
while True:
	ret, img2 = cap.read()

	#kp1, des1 = sift.detectAndCompute(img1,None)
	kp2, des2 = sift.detectAndCompute(img2,None)

	flann = cv2.FlannBasedMatcher(index_params, search_params)

	matches = flann.knnMatch(des1,des2,k=2)


	good = []
	for m,n in matches:
	    if m.distance < 0.7*n.distance:
	        good.append(m)
	if len(good)>MIN_MATCH_COUNT:
	    src_pts = np.float32([ kp1[m.queryIdx].pt for m in good ]).reshape(-1,1,2)
	    dst_pts = np.float32([ kp2[m.trainIdx].pt for m in good ]).reshape(-1,1,2)

	    M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC,3.0)
	    matchesMask = mask.ravel().tolist()

	    #h,w = img1.shape
	    #pts = np.float32([ [0,0],[0,h-1],[w-1,h-1],[w-1,0] ]).reshape(-1,1,2)
	    
	    if M is not None:
	    	dst = cv2.perspectiveTransform(pts,M)
	    	if len(dst)==4:
	    		img2 = cv2.polylines(img2,[np.int32(dst)],True,(0,255,0),3, cv2.LINE_AA)
	    		cv2.imshow('img2',img2)
	else:
	    print ("Not enough matches are found - %d/%d" % (len(good),MIN_MATCH_COUNT))
	    matchesMask = None


		
	if cv2.waitKey(1) & 0xFF == ord('q'):
		cap.release()
		cv2.destroyAllWindows()
		break