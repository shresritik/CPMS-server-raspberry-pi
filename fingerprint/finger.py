# finger.templates not updating values after delete() is called
# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import time
import board
import busio
from digitalio import DigitalInOut, Direction
import adafruit_fingerprint
import random

led = DigitalInOut(board.D13)
led.direction = Direction.OUTPUT

# Commented
# uart = busio.UART(board.TX, board.RX, baudrate=57600)

# If using with a computer such as Linux/RaspberryPi, Mac, Windows with USB/serial converter:
import serial
try:
  uart = serial.Serial("/dev/ttyUSB0", baudrate=57600, timeout=1)
except:
  uart = serial.Serial("/dev/ttyUSB1", baudrate=57600, timeout=1)

# If using with Linux/Raspberry Pi and hardware UART:
# import serial
# uart = serial.Serial("/dev/ttyS0", baudrate=57600, timeout=1)

finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)
# enrolled_ids = finger.templates.copy()	   # err: 'finger.templates' not updating on enroll/delete
##################################################


def get_fingerprint():
    """Get a finger print image, template it, and see if it matches!"""
    print("Waiting for image...")
    while finger.get_image() != adafruit_fingerprint.OK:
        pass
    print("Templating...")
    if finger.image_2_tz(1) != adafruit_fingerprint.OK:
        return False
    print("Searching...")
    if finger.finger_search() != adafruit_fingerprint.OK:
        return False
    return True


# pylint: disable=too-many-branches
def get_fingerprint_detail():
    """Get a finger print image, template it, and see if it matches!
    This time, print out each error instead of just returning on failure"""
    print("Getting image...", end="")
    i = finger.get_image()
    if i == adafruit_fingerprint.OK:
        print("Image taken")
    else:
        if i == adafruit_fingerprint.NOFINGER:
            print("No finger detected")
        elif i == adafruit_fingerprint.IMAGEFAIL:
            print("Imaging error")
        else:
            print("Other error")
        return False

    print("Templating...", end="")
    i = finger.image_2_tz(1)
    if i == adafruit_fingerprint.OK:
        print("Templated")
    else:
        if i == adafruit_fingerprint.IMAGEMESS:
            print("Image too messy")
        elif i == adafruit_fingerprint.FEATUREFAIL:
            print("Could not identify features")
        elif i == adafruit_fingerprint.INVALIDIMAGE:
            print("Image invalid")
        else:
            print("Other error")
        return False

    print("Searching...", end="")
    i = finger.finger_fast_search()
    # pylint: disable=no-else-return
    # This block needs to be refactored when it can be tested.
    if i == adafruit_fingerprint.OK:
        print("Found fingerprint!")
        return True
    else:
        if i == adafruit_fingerprint.NOTFOUND:
            print("No match found")
        else:
            print("Other error")
        return False


# pylint: disable=too-many-statements
def enroll_finger(location=-1):
    """Take a 2 finger images and template it, then store in 'location'"""
    for fingerimg in range(1, 3):
        if fingerimg == 1:
            print("Place finger on sensor...", end="")
        else:
            print("Place same finger again...", end="")
            
        while True:
            i = finger.get_image()
            if i == adafruit_fingerprint.OK:
                print("Image taken")
                break
            if i == adafruit_fingerprint.NOFINGER:
                print(".", end="")
            elif i == adafruit_fingerprint.IMAGEFAIL:
                print("Imaging error")
                return False
            else:
                print("Other error")
                return False

        print("Templating...", end="")
        i = finger.image_2_tz(fingerimg)
        
        if i == adafruit_fingerprint.OK:
            print("Templated")
            if fingerimg == 1 and finger.finger_search() == adafruit_fingerprint.OK:
                print('Fingerprint Already Exists, #id:{}'.format(finger.finger_id))
                return finger.finger_id
        else:
            if i == adafruit_fingerprint.IMAGEMESS:
                print("Image too messy")
            elif i == adafruit_fingerprint.FEATUREFAIL:
                print("Could not identify features")
            elif i == adafruit_fingerprint.INVALIDIMAGE:
                print("Image invalid")
            else:
                print("Other error")
            return False

        if fingerimg == 1:
            print("Remove finger")
            time.sleep(1)
            while i != adafruit_fingerprint.NOFINGER:
                i = finger.get_image()

    print("Creating model...", end="")
    i = finger.create_model()
    if i == adafruit_fingerprint.OK:
        print("Created")
    else:
        if i == adafruit_fingerprint.ENROLLMISMATCH:
            print("Prints did not match")
        else:
            print("Other error")
        return False

    print("Storing model #%d..." % location, end="")
    i = finger.store_model(location)
    if i == adafruit_fingerprint.OK:
        print("Stored")
    else:
        if i == adafruit_fingerprint.BADLOCATION:
            print("Bad storage location")
        elif i == adafruit_fingerprint.FLASHERR:
            print("Flash storage error")
        else:
            print("Other error")
        return False

    return location


##################################################


def get_num():
    """Use input() to get a valid number from 1 to 127. Retry till success!"""
    i = 0
    while (i > 127) or (i < 1):
        try:
            i = int(input("Enter ID # from 1-127: "))
        except ValueError:
            pass
    return i

if finger.read_templates() != adafruit_fingerprint.OK:
    raise RuntimeError("Failed to read templates")

if __name__=="__main__":
    while True:
        print("----------------")
        #if finger.read_templates() != adafruit_fingerprint.OK:
        #    raise RuntimeError("Failed to read templates")
        print("Fingerprint templates:", finger.templates)
        print("e) enroll print")
        print("f) find print")
        print("d) delete print")
        print("----------------")
        c = input("> ")

        if c == "e":
            enroll_finger(get_num())
            # update finger object
            finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)
        if c == "f":
            if get_fingerprint():
                print("Detected #", finger.finger_id, "with confidence", finger.confidence)
            else:
                print("Finger not found")
        if c == "d":
            if finger.delete_model(get_num()) == adafruit_fingerprint.OK:
                # update finger object
                finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)
                
                print("Deleted!")


# code for backend
# Find
# finger_location = enroll_finger(location:<optional int>)
def enroll():
        # random enroll id location
        enroll_id = random.choice([i for i in range(1,128) if i not in finger.templates])
        enroll_id = enroll_finger(enroll_id)
        # update finger object
        # finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)
        # enrolled_ids.append(enroll_id)
        
        print(f'id: {enroll_id}')
        return {'id': enroll_id}
def find():
    if get_fingerprint():
        print("Detected #", finger.finger_id, "with confidence", finger.confidence)
        return {'id': finger.finger_id, 'confidence': finger.confidence}
    else:
        detected = False
        print("Finger not found")
    return False

def delete(id = -1):
    # delete fingerprint id if id is given
    # scan and delete if id not given
    global finger
    if id == -1:
        print("No id given so scanning to get id to delete")
        if not get_fingerprint():
            print("Not Enrolled")
            return False
        else:
            print(f'Finger found at id:{finger.finger_id}')
            id = finger.finger_id
    if finger.delete_model(id) == adafruit_fingerprint.OK:
        # update finger object
        # finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)
        # enrolled_ids.remove(id)
        return {'id': id}
    else:
        print("Failed to delete")

def list_enrolled():
    # lists fingerprints enrolled
    return finger.templates
    # return enrolled_ids
