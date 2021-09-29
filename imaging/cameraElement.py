#---------------------------------------------------------------------------------------
#Manages Camera Timing & Image transmission

import os
import os.path
import sys

#set proper path for modules
sys.path.append('/home/pi/oasis-grow')
sys.path.append('/usr/lib/python37.zip')
sys.path.append('/usr/lib/python3.7')
sys.path.append('/usr/lib/python3.7/lib-dynload')
sys.path.append('/home/pi/.local/lib/python3.7/site-packages')
sys.path.append('/usr/local/lib/python3.7/dist-packages')
sys.path.append('/usr/lib/python3/dist-packages')

#import libraries
import time
import base64
import PIL
from PIL import Image
from subprocess import Popen
import requests
import json
import pyrebase

#declare state variables
device_state = None #describes the current state of the system
feature_toggles = None #holds feature toggles
access_config = None #contains credentials for connecting to firebase

#declare state variables
device_state = None #describes the current state of the system
grow_params = None #describes the grow configuration of the system
hardware_config = None #holds hardware I/O setting & pin #s
access_config = None #contains credentials for connecting to firebase
feature_toggles = None #tells the system which features are in use

def load_state(loop_limit=100000): #Depends on: 'json'; Modifies: device_state,hardware_config ,access_config
    global device_state, feature_toggles, access_config, grow_params, hardware_config

    for i in list(range(int(loop_limit))): #try to load, check if available, make unavailable if so, write state if so, write availabke iff so,  
        try:
            with open("/home/pi/oasis-grow/configs/device_state.json") as d:
                device_state = json.load(d) #get device state    
                
            with open("/home/pi/oasis-grow/configs/grow_params.json") as g:
                grow_params = json.load(g) #get grow params   
                
            with open("/home/pi/oasis-grow/configs/access_config.json") as a:
                access_config = json.load(a) #get access state
                
            with open ("/home/pi/oasis-grow/configs/feature_toggles.json") as f:
                feature_toggles = json.load(f) #get feature toggles
        
            with open ("/home/pi/oasis-grow/configs/hardware_config.json") as h:
                hardware_config = json.load(h) #get hardware config
        
            break
            
        except Exception as e:
            print("Error occured while camera reading. Retrying...")

#modifies a firebase variable
def patch_firebase(field,value): #Depends on: load_state(),'requests','json'; Modifies: database['field'], state variables
    load_state()
    data = json.dumps({field: value})
    url = "https://oasis-1757f.firebaseio.com/"+str(access_config["local_id"])+"/"+str(access_config["device_name"])+".json?auth="+str(access_config["id_token"])
    result = requests.patch(url,data)

def initialize_user(refresh_token):
#app configuration information
    config = {"apiKey": "AIzaSyD-szNCnHbvC176y5K6haapY1J7or8XtKc",
              "authDomain": "oasis-1757f.firebaseapp.com",
              "databaseURL": "https://oasis-1757f.firebaseio.com/",
              "storageBucket": "oasis-1757f.appspot.com"
             }

    firebase = pyrebase.initialize_app(config)
    auth = firebase.auth()
    db = firebase.database()
    user = auth.refresh(refresh_token)
    storage = firebase.storage()

    return user, db, storage

def send_image(user, storage, path):
    #send new image to firebase
    storage.child(user['userId'] + "/" + access_config["device_name"] + "/image.jpg").put(path, user['idToken'])
    print("sent image")

    #tell firebase that there is a new image
    patch_firebase("new_image","1")
    print("firebase has an image in waiting")

def take_picture(image_path):
    #take picture and save to standard location
    still = Popen(["sudo", "raspistill", "-o", str(image_path)]) #snap: call the camera
    still.wait()

def save_to_feed(image_path):
    #timestamp image
    timestamp = time.time()
    #move timestamped image into feed
    save_most_recent = Popen(["sudo", "cp", str(image_path), "/home/pi/oasis-grow/data_out/image_feed/culture_image" + str(timestamp)+'.jpg'])
    save_most_recent.wait()

#define a function to actuate element
def actuate(interval): #amount of time between shots in minutes
    load_state()
    take_picture('/home/pi/image.jpg')

    if feature_toggles["save_images"] == "1":
        save_to_feed('/home/pi/image.jpg')

    if device_state["connected"] == "1":

        #get user info
        user, db, storage = initialize_user(access_config["refresh_token"])
        print("got credentials")

        #send new image to firebase
        send_image(user, storage, '/home/pi/image.jpg')

    time.sleep(float(interval)*60)

if __name__ == '__main__':
    try:
        actuate(str(sys.argv[1]))
    except KeyboardInterrupt:
        print("Interrupted")

