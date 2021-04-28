#!/usr/bin/env python3

#Tutorial Link: https://www.pyimagesearch.com/2020/08/31/image-alignment-and-registration-with-opencv/

#This tutorial goes over how to perform image alignemnt and registration which is aligning pictures of
#the same thing taken from difference perspectives


import numpy as np
import imutils
import cv2

def align_images(image, template, maxFeatures=500, nt=0.2, debug=False):
    imageGray  = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    templateGray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    # use ORB to detect keypoints and extract (binary) local
    # invariant features
    orb = cv2.ORB_create(maxFeatures)
    (kpsA, descsA) = orb.detectAndCompute(imageGray, None)
    (kpsB, descsB) = orb.detectAndCompute(templateGray, None)
    #print(kpsA[0].pt)
    # match the features
    method = cv2.DESCRIPTOR_MATCHER_BRUTEFORCE_HAMMING
    matcher = cv2.DescriptorMatcher_create(method)
    matches = matcher.match(descsA, descsB, None)
    #print(matches[0].distance)
    #print(matches[0].imgIdx)
    #print(matches[0].queryIdx)
    #print(matches[0].trainIdx)
    # sort the matches by their distance (the smaller the distance,
    # the "more similar" the features are)
    matches = sorted(matches, key=lambda x:x.distance)
    '''
    best = matches[4]
    bq = best.queryIdx
    bi = best.imgIdx
    bt = best.trainIdx
    bq_pt = kpsA[bq].pt
    bt_pt = kpsB[bt].pt
    #bi_pt = kpsB[bi].pt
    print(bi)

    print(bq_pt)
    print(bt_pt)
    x,y = bq_pt
    x2,y2 = bt_pt'''
    #x3,y3 = bi_pt

    #cv2.circle(image, (int(x),int(y)), 20, (0,0,255), -1)
    #cv2.circle(template, (int(x2),int(y2)), 20, (0,0,255), -1)
    #cv2.circle(template, (int(x3),int(y3)), 20, (0,0,255), -1)

    # keep only the top matches
    keep = int(len(matches) * nt)
    matches = matches[:keep]
    # check to see if we should visualize the matched keypoints
    if debug:
        matchedVis = cv2.drawMatches(image, kpsA, template, kpsB,
            matches, None)
        matchedVis = imutils.resize(matchedVis, width=1000)
        cv2.imshow("Matched Keypoints", matchedVis)
        cv2.waitKey(0)


    # allocate memory for the keypoints (x, y)-coordinates from the
    # top matches -- we'll use these coordinates to compute our
    # homography matrix
    ptsA = np.zeros((len(matches), 2), dtype="float")
    ptsB = np.zeros((len(matches), 2), dtype="float")
    # loop over the top matches
    for (i, m) in enumerate(matches):
        # indicate that the two keypoints in the respective images
        # map to each other
        ptsA[i] = kpsA[m.queryIdx].pt
        ptsB[i] = kpsB[m.trainIdx].pt

    #print(ptsA[0])
    #print(ptsB[0])


    # compute the homography matrix between the two sets of matched
    # points
    (H, mask) = cv2.findHomography(ptsA, ptsB, method=cv2.RANSAC)
    # use the homography matrix to align the images
    (h, w) = template.shape[:2]
    aligned = cv2.warpPerspective(image, H, (w, h))
    # return the aligned image
    #aligned_v = imutils.resize(aligned, width=1000)
    #template_v = imutils.resize(template, width=1000)
    #cv2.imshow("warped", aligned_v)
    #cv2.imshow("template",template_v)
    #cv2.waitKey(0)

    return aligned


def driver():
    im1 = cv2.imread('side1.jpg')
    #template
    template = cv2.imread('side2.jpg')

    aligned_im = align_images(im1,template,debug=False)

     # resize both the aligned and template images so we can easily
    # visualize them on our screen
    aligned = imutils.resize(aligned_im, width=700)
    template = imutils.resize(template, width=700)
    # our first output visualization of the image alignment will be a
    # side-by-side comparison of the output aligned image and the
    # templates
    stacked = np.hstack([aligned, template])

    # our second image alignment visualization will be *overlaying* the
    # aligned image on the template, that way we can obtain an idea of
    # how good our image alignment is
    overlay = template.copy()
    output = aligned.copy()
    cv2.addWeighted(overlay, 0.5, output, 0.5, 0, output)
    # show the two output image alignment visualizations
    cv2.imshow("Image Alignment Stacked", stacked)
    cv2.imshow("Image Alignment Overlay", output)
    cv2.waitKey(0)




if __name__ == "__main__":
    driver()
