
import subprocess
import time
import os
import cv2
import numpy as np
import winsound
import threading
import gspread

from oauth2client.service_account import ServiceAccountCredentials


#Video Stream for windows
class VideoStream:

    #Constructor Class
    def __init__(self, src):
        self.stream = cv2.VideoCapture(src)     #Stream of frames
        # self.stream.set(cv2.CAP_PROP_EXPOSURE, -2)      #Set camera settings
        (self.grabbed,self.frame) = self.stream.read()     #Frame of camera when class is constructed and boolean stating frame successfully grabbed
        self.stopped = False            #Boolean for whether video stream is 


    #Function to start the threead of the Video Stream
    def start(self):
        threading.Thread(target=self.update, args=()).start()
        return self
    
    #Function to continuously get frames
    def update(self):
        while True:
            (self.grabbed,self.frame) = self.stream.read()
            cv2.imshow("Camera 0", self.frame)
            if cv2.waitKey(1) == ord("q"):
                break
        self.stop_process()
    #Read the current frame
    def read(self):
        return self.grabbed,self.frame
            
    #Release the associated resources
    def stop_process(self):
        self.stream.release()
        self.stopped = True

#Optical Character Recognizer
class OCR:

    #Constructor for ocr
    def __init__(self):

        self.exchange = None
        self.stopped = False
        self.img = None

    #Start thread for ocr
    def start(self):
        threading.Thread(target=self.ocr, args=()).start()
        return self
    
    #Set the exchanged frame
    def set_exchange(self, video_stream):
        self.exchange = video_stream

    #Grab image for ocr scanner
    def read(self):
        return self.exchange.grabbed,self.img

    def stop_process(self):
        self.exchange.stream.release()
        self.stopped = True

    def ocr(self):
        detector = cv2.QRCodeDetector()

        while not self.stopped:
            if self.exchange is not None:
                self.img = self.exchange.frame #Set image to frame of Video stream
                data, bbox, _ = detector.detectAndDecode(self.img)

            self.stopped = self.exchange.stopped
#^ GOOGLE SHEETS STUFF
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
json_path = "C:\Repos\QRScout\QRScoutScanner\qrscoutdatamanager-fd7fbe7526ef.json"
if not os.path.exists(json_path):
    raise FileNotFoundError(f"Error: JSON file not found at {json_path}")

creds = ServiceAccountCredentials.from_json_keyfile_name(json_path, SCOPE)
client = gspread.authorize(creds)
if client:
    print("client Works!")
try:
    sheet = client.open("Reefscape Scouter Spreadsheet").sheet1
except gspread.exceptions.SpreadsheetNotFound:
    raise ValueError("Error: Google Sheet 'Reefscape Scouter Spreadsheet' not found. Check the name or share settings.")



def update_google_sheet(sheet, qr_data):
    if not qr_data:
        return  # Skip empty data
    
    try:
        sheet.append_row([qr_data])
        print(f"Successfully added to Google Sheets: {qr_data}")
    except Exception as e:
        print(f"Error updating Google Sheets: {e}")


def openQRScanner(filePath):

    frames = VideoStream(0).start()     #Start Video Capture thread
    cap = OCR().start()                 #Start OCR thread
    cap.set_exchange(frames)            #Start copying video capture frames to ocr
    detector = cv2.QRCodeDetector()     #Create QR code detector 
    
    prev_qr_arrays = [None]
    #QR Scanner loop, breaks when you hit 'q'

    while True:
        
        # k = cv2.waitKey(100)
        _, frame = frames.read()
        # b,img = cap.read()
        qr_array = None

        if cv2.waitKey(1) == ord("q"):
                frames.stop_process()
                cap.stop_process()
                cv2.destroyAllWindows()
                break  
        #If qr code is defective, try again
        print("Grabbed",_)
        # try:
        #     data, bbox, b = detector.detectAndDecode(img)
        # except Exception as e:
        #     print("Scanner Problem, please wait for it to reset")
        #     continue
        # if data:
        #     #If data isn't a string, continue
        #     try:
        #         qr_array=str(data)
        #     except Exception as e:
        #         print("An Error Has Occured, Please make sure the QR code returns a string\n")
        #         print("5 second delay, please remove faulty QR code:\n")
        #         for i in range(5,0,-1):
        #             print(i + "\n")
        #         print("Resuming program...")
        #         continue
            
        #Open window with camera, close by pressing 'q' key
        # cv2.imshow("Camera 1", frame)
        if cv2.waitKey(1) == ord("q"):
                cap.stop_process()
                frames.stop_process()
                cv2.destroyAllWindows()
                break  

        #Write qr_arraying to allStrings, and prevent repeats
        with open(filePath, 'r') as file:
            lines = file.readlines()
            if (qr_array == None) or (qr_array +'\n' in lines):
               continue
        with open(filePath, 'a') as file:
            file.write(qr_array + '\n')
        #Paste string and beep confirmation
        print(qr_array)
        
        prev_qr_arrays.append(qr_array)
        winsound.Beep(2500,500)
        time.sleep(0.5)
    cv2.destroyAllWindows()


if __name__ == '__main__':

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_EXPOSURE, -2)      #Set camera settings

    # initialize the cv2 QRCode detector 
    detector = cv2.QRCodeDetector()
    prev_qr_arrays = [None]

    while True: 
        is_grabbed, img = cap.read()
        qr_array = [None]


        cv2.imshow("Cam1", img)
        if cv2.waitKey(1) == ord("q"):
            break

        try:
            data, bbox, b = detector.detectAndDecode(img)
        except Exception as e:
            print("Scanner Problem, please wait for it to reset")
            continue
        if data:
            #If data isn't a string, continue
            try:
                qr_array=str(data)
                print(data)
            except Exception as e:
                print("An Error Has Occured, Please make sure the QR code returns a string\n")
                print("5 second delay, please remove faulty QR code:\n")
                for i in range(5,0,-1):
                    print(i + "\n")
                    time.sleep(1)
                print("Resuming program...")
                continue
        
        if (qr_array == None):
            continue
        elif qr_array in prev_qr_arrays:
            winsound.Beep(2000, 500)
            winsound.Beep(1500, 500)
            continue

        print(qr_array)
        """
        DATA ARRAY EXPLANATION:

        Initials for scouter,
        


        """
        prev_qr_arrays.append(qr_array)
        update_google_sheet(sheet, qr_array)
        winsound.Beep(2500,500)
        time.sleep(1.0)

    cap.release()
    cv2.destroyAllWindows()