import cv2
import numpy as np
import os
import Handtracking as htm

brushThickness = 20
eraserThickness = 100

xp, yp = 0, 0

folder_path = "headers"
mylist = os.listdir(folder_path)

def extract_num(filename):
    return int(''.join(filter(str.isdigit, filename)))

# Sort the list using the extracted numerical part
mylist.sort(key=extract_num)

overlaylist = []

for impath in mylist:
    image = cv2.imread(f"{folder_path}/{impath}")
    overlaylist.append(image)

# Initial header and drawing color
header = overlaylist[0]
drawColor = (255, 0, 255)  # Default color

detector = htm.handDetector(detectionCon=0.85)
imgCanvas = np.zeros((720, 1280, 3), np.uint8)

cap = cv2.VideoCapture(0)

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)

    # Find hand landmarks
    img = detector.findHands(img)
    lmlist = detector.findPosition(img, draw=False)

    if len(lmlist) != 0:


        # Index finger
        x1, y1 = lmlist[8][1:]
        # Middle finger
        x2, y2 = lmlist[12][1:]

        # Check if fingers are up
        fingers = detector.fingers()
        # print(fingers)

        # If it is selection mode
        if fingers[1] and fingers[2]:
            xp, yp = 0, 0
            print("Selection Mode")
            # Checking for the click
            if y1 < 125:
                if 250 < x1 < 450:
                    header = overlaylist[0]
                    drawColor = (255, 0, 255)
                elif 550 < x1 < 750:
                    header = overlaylist[1]
                    drawColor = (255, 0, 0)
                elif 800 < x1 < 950:
                    header = overlaylist[2]
                    drawColor = (0, 255, 0)
                elif 1050 < x1 < 1200:
                    header = overlaylist[3]
                    drawColor = (0, 0, 0)

            cv2.rectangle(img, (x1, y1 - 25), (x2, y2 + 25), drawColor, cv2.FILLED)

        # If it is drawing mode
        if fingers[1] and not fingers[2]:
            cv2.circle(img, (x1, y1), 15, drawColor, cv2.FILLED)
            print("Drawing Mode")
            if xp == 0 and yp == 0:
                xp, yp = x1, y1

            if drawColor==(0,0,0):
                cv2.line(img, (xp, yp), (x1, y1), drawColor, eraserThickness)
                cv2.line(imgCanvas, (xp, yp), (x1, y1), drawColor, eraserThickness)
            else:


                cv2.line(img, (xp, yp), (x1, y1), drawColor, brushThickness)
                cv2.line(imgCanvas, (xp, yp), (x1, y1), drawColor, brushThickness)
            xp, yp = x1, y1

    # Resize the header if necessary to ensure it matches the width of the captured image
    header_resized = cv2.resize(header, (img.shape[1], 125))

    # Place the header image at the top of the frame
    img[0:125, 0:img.shape[1]] = header_resized

    # Merge the canvas with the webcam image
    imgGray = cv2.cvtColor(imgCanvas, cv2.COLOR_BGR2GRAY)
    _, imgInv = cv2.threshold(imgGray, 50, 255, cv2.THRESH_BINARY_INV)
    imgInv = cv2.cvtColor(imgInv, cv2.COLOR_GRAY2BGR)
    img = cv2.bitwise_and(img, imgInv)
    img = cv2.bitwise_or(img, imgCanvas)

    cv2.imshow("image", img)
    cv2.imshow("canvas", imgCanvas)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
