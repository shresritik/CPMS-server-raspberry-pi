from fastapi import FastAPI, Depends, File, UploadFile
from fastapi.responses import FileResponse
from yolov5_tflite_webcam_inference import detect_video
from fastapi.middleware.cors import CORSMiddleware
import os
from sqlalchemy.orm import Session
from sqlalchemy import desc
import base64
from db.config import engine, SessionLocal
import db.model as model
import db.schemas as schemas
import aiofiles
import datetime
import uuid
from fastapi.staticfiles import StaticFiles
# from fingerprint import finger

model.Base.metadata.create_all(bind=engine)
app = FastAPI()

# to access Uploaded Image
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


# Import Fingerprint code
try:
    from fingerprint import finger
except Exception as ex:
    print('\n\n Error Importing Fingerprint Module: ', ex)

origins = [
    "http://127.0.0.1:5173",
    "http://localhost:5173",
    "http://localhost:8080",
    "*"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# listDir = os.getcwd()

BASE_PATH = os.getcwd()
print(BASE_PATH)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/api/v1/upload/")
async def root():

    value = detect_video(weights=BASE_PATH+"/models/custom_plate.tflite", labels=BASE_PATH+"/labels/plate.txt", conf_thres=0.25, iou_thres=0.45,
                         img_size=640, webcam=0)

    print("inside main", value)
    # file_path = listDir + '\output\cropped\cropped1.jpg'
    with open(BASE_PATH+"/output/cropped/cropped1.jpg", "rb") as image2string:
        converted_string = base64.b64encode(image2string.read())
    # file = FileResponse(file_path, media_type='image/jpeg')
    return {"message": value, "file": converted_string}


@app.post("/api/v1/upload/")
async def publish(request: schemas.UserCreate, db: Session = Depends(get_db)):
    new_user = model.User(numOfPass=request.numOfPass,
                          plateImg=request.plateImg, numberPlate=request.numberPlate, licenseImg=request.licenseImg, expiry_date=request.expiry_date)
    print(new_user)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.get("/api/v1/")
async def getAll(db: Session = Depends(get_db)):

    users = db.query(model.User).order_by(desc(model.User.id)).all()
    print(users)
    return users


@app.delete("/api/v1/delete/{id}")
async def deleteId(id, db: Session = Depends(get_db)):

    db.query(model.User).filter(
        model.User.id == id).delete(synchronize_session=False)
    db.commit()
    return {"deleted": "true"}

# --------------------------------
# Fingerprint api
# --------------------------------


@app.post("/api/v1/new_driver/")
async def new_driver(username: str, expiry_date: str, license_img: UploadFile, db: Session = Depends(get_db)):
    # Create new driver
    # print(f"\n\nrequest: {request}")
    file_extension = license_img.filename.split(".")[-1]
    file_name = f"/uploads/{uuid.uuid4()}.{file_extension}"
    print('\n\nfile_name: ', file_name)
    # user_dir = f"./uploads/{request.username}"
    os.makedirs("./uploads", exist_ok=True)
    async with aiofiles.open(f"{'.'+file_name}", 'wb') as out_file:
        content = await license_img.read()  # Read the contents of the file
        await out_file.write(content)  # Write the contents to the new file

    try:
        # enroll a new user with fingerprint sensor
        finger_id = finger.enroll()['id']
    except Exception as ex:
        finger_id = -1
        print(f'\n\n Error Importing Fingeprint : {ex} ')

    new_driver = model.Driver(username=username,
                              license_img=file_name, expiry_date=expiry_date, finger_id=finger_id)
    db.add(new_driver)
    db.commit()
    db.refresh(new_driver)
    return new_driver

# Search and validate one driver by scanning fingerprint


@app.get("/api/v1/validate_driver/")
async def getDriver(db: Session = Depends(get_db)):
    # e.g. http://localhost:8000/api/v1/driver/11
    # GEt one driver
    print(f"driver: {model.Driver}")
    # driver = db.query(model.Driver).order_by(
    #     desc(model.Driver.id)).all()
    # driver = db.query(model.Driver).filter_by(finger_id=id).first()

    # find fingerprint
    try:
        # enroll a new user with fingerprint sensor
        finger_id = finger.find()['id']
    except Exception as ex:
        finger_id = -1
        print(f'\n\n Error Importing Fingeprint : {ex} ')
        return {'driver': None, 'message': 'Error Importing Fingeprint : {}'.format(ex)}

    # search by fingerprint id
    try:
        driver = db.query(model.Driver).filter(
            model.Driver.finger_id == finger_id).first()
        print(f"\n\n driver expiry: {driver.expiry_date}")
    except:
        return {'driver': None, 'message': 'No driver found with finger id :{}'.format(finger_id)}

    # Validating expiry date
    print('\n\ndriver: {}\n\n'.format(driver))
    seperator = driver.expiry_date
    date = tuple([int(a) for a in driver.expiry_date.split(seperator[4])])
    license_expiry = datetime.datetime(date[0], date[1], date[2])
    if license_expiry < datetime.datetime.now():
        return {'driver': driver, 'message': 'License Expired! Please renew it!'}

    return {'driver': driver, 'message': 'Valid license Found!'}

# List of all drivers


@app.get("/api/v1/drivers/")
async def getAllDrivers(db: Session = Depends(get_db)):
    # Get all the drivers
    print(f"driver: {model.Driver}")
    drivers = db.query(model.Driver).order_by(desc(model.Driver.id)).all()
    return drivers

# Delete one driver by scanning fingerprint


@app.delete("/api/v1/delete_driver/")
async def deleteId(id, db: Session = Depends(get_db)):
    # Find driver by scanning finger
    try:
        # enroll a new user with fingerprint sensor
        finger_id = finger.find()['id']
    except Exception as ex:
        finger_id = -1
        print(f'\n\n Error Importing Fingeprint : {ex} ')
        return {'deleted': False, 'message': 'Error Importing Fingeprint : {}'.format(ex)}

    # delete fingerprint data from fingerprint sensor
    finger_id = finger.delete()['id']

    # search by fingerprint id in database
    try:
        driver = db.query(model.Driver).filter(
            model.Driver.finger_id == finger_id).first()
        print(f"\n\n driver: {driver.expiry_date}")
    except:
        return {'deleted': False, 'message': 'No driver found with finger id :{}'.format(finger_id)}

    # delete image from /uploads
    image_location = './' + driver['license_img']
    image_location.replace('//', '/')
    print(image_location)
    if os.path.exists(image_location):
        os.rmdir('image_location')
    else:
        print("\n\n TODO  delete image from location: \'{}\' \n\n".format(
            image_location))

    # delete data from database
    if finger_id:
        db.query(model.Driver).filter(
            model.Driver.finger_id == id).delete(synchronize_session=False)
        driver_to_delete = db.query(model.Driver).filter(
            model.Driver.finger_id == finger_id).first()
        db.commit()
        return {"deleted": True, 'message': 'deleted successfully: {}'.format(driver)}
    else:
        return {"deleted": False, 'message': 'did not find matching finger_id: {}'.format(finger_id)}
