# Connect to hidden wifi network
sudo nano /etc/wpa_supplicant/wpa_supplicant.conf


# ----------------------------------
# Fingerprint_Code
# ---------------------------------- 

# to reload the imported model
import importlib
import finger				# importing finger.py
importlib.reload(finger)	# Do this after enroll and delete

# example:
import importlib
import finger

finger.list_enrolled()	# returns list of integers

# To enroll new user
finger.enroll()		# returns: {'id': enroll_id}
importlib.reload(finger)	# Do this after enroll and delete

# To delete enrolled template with id 11
finger.delete(11)	# returns: False or {'deleted': True, id: id}
importlib.reload(finger)	# Do this after enroll and delete

finger.list_enrolled()	# list enrolled users
finger.find()	# returns {'id': 78, 'confidence': 80}

# References:
https://learn.adafruit.com/adafruit-optical-fingerprint-sensor/circuitpython
