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
model.Base.metadata.create_all(bind=engine)
app = FastAPI()

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
                          plateImg=request.plateImg, numberPlate=request.numberPlate)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.get("/api/v1/")
async def getAll(db: Session = Depends(get_db)):

    users = db.query(model.User).order_by(desc(model.User.id)).all()
    return users


@app.delete("/api/v1/delete/{id}")
async def deleteId(id, db: Session = Depends(get_db)):

    db.query(model.User).filter(
        model.User.id == id).delete(synchronize_session=False)
    db.commit()
    return {"deleted": "true"}
