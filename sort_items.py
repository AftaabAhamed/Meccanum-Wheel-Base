import cv2
import json
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import serial
from time import sleep
import time
# initalize the cam
cap = cv2.VideoCapture(0)
# initialize the cv2 QRCode detector
detector = cv2.QRCodeDetector()
ser = serial.Serial('/dev/ttyUSB0')
ser.baudrate = 115200
cred = credentials.Certificate('account_key.json')
firebase_admin.initialize_app(cred, {
    'projectId': 'autonomous-shopping-cart-4bb0a',
})

previous_state = None
# Get a reference to the Firestore database
db = firestore.client()

def send_fbase(data_str):
# Parse the JSON string into a Python dictionary
    data = json.loads(data_str)
    # Add the data to a Firestore collection
    doc_ref = db.collection('Products').document()
    doc_ref.set(data)

    print(f"Document added with ID: {doc_ref.id}")
    sort_item(data)

def check_payment():
# def check_boolean_value():
    global previous_state
    doc_ref = db.collection('finshop').document('IsComplete')
    doc = doc_ref.get()
    if doc.exists:
        data = doc.to_dict()
        boolean_value = data.get('booleanField', False)
        print(f"Boolean value: {boolean_value}")
        return(boolean_value)

    else:
        print("Document does not exist")
        return(False)
    

def sort_item(data):
    #open top 
    print(data)
    if data["Category"] == "Soft":
        ser.write(b's')
        sleep(5)
    elif data["Category"] == 'Hard':
        ser.write(b'h')
        sleep(5)
        print("is it hard")

def open_cart():
    ser.write(b'o')
    sleep(15)
    ser.write(b'c')


time_interval = 2
prev_time = time.time()
prev_det_time = time.time()
while cap.isOpened():

    _, img = cap.read()
    # detect and decode
    data, bbox, _ = detector.detectAndDecode(img)
    # check if there is a QRCode in the image
    curr_det_time = time.time()
    if data and ((curr_det_time-prev_det_time)>15):
        a=data
        send_fbase(data)
    
    curr_time = time.time()

    if ((curr_time-prev_time)>time_interval):
        if (check_payment()):
            open_cart()
        prev_time = curr_time

    # display the result
    cv2.imshow("QRCODEscanner", img)    
    if cv2.waitKey(1) == ord("q"):
        break    # display the result    # display the result

cap.release()
cv2.destroyAllWindows()