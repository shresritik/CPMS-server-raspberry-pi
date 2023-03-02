# Fingerprint Working
## api/v1/new_driver: <method: POST>
* Input Data: None
    - username <string>
    - expiry_date <string: 2022/02/22>
    - license_img <image>

* returns: {'driver': None, 'message': 'No driver found with finger id :{}'.format(finger_id)}

* Working:
  - user scans fingerprint : return fingerprint_id if user exists else store fingerprint template with random id and return id
  - store fingerprint_id, license_image_url, username, license_expiry date in database

## api/v1/validate_driver: <method: get>
* Input Data: None
* Description: validates drivers license expiry by thumb-scan
* returns  
  <obj: driver> = 
    username: string
    license_img: url
    expiry_date: string
    finger_id: integer

* Working:
  - re-scan finger-print untill match and get fingerprint_id
  - find data associated with fingerprint id in database
  - check if license has expired by comparing with current date
  - return whether or not  license has expired

## api/v1/drivers: <method: get>
* description: gets list of all saved drivers
* returns list<driver>
* working:
  - query database and return data

## api/v1/delete_driver/{id} : <method: delete>
* deletes driver with given fingerprint id
* returns {"deleted": True, 'message': 'success/error message'}
* working:
  - Find fingerprint id by scanning fingerprint of user
  - find and delete associated license_image
  - delete associated data from database
  - delete stored fingerprint template

# Todo:
finger_id = -1
        while finger_id == -1:
            finger_id = finger.find() # enroll a new user with fingerprint sensor
            if 'id' in finger_id.keys() and type(finger_id) == dict:
                finger_id = finger_id['id']