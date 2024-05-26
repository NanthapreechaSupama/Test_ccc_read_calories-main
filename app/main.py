import easyocr
import time
from fastapi import FastAPI, Request, Body
from fastapi.middleware.cors import CORSMiddleware
import cv2
import requests
import base64
import numpy as np
from typing import Union
from pydantic import BaseModel

reader = easyocr.Reader(["th", "en"])
app = FastAPI()

origins = [
    "https://ccc.mots.go.th",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Item(BaseModel):
    base64str: str


def dist(p, q):
    if abs(p[1]-q[1])<5:
        return 0
    return ((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2) ** 0.5


def base64_to_image(img_bs64: str) -> np.ndarray:
    byte_image = base64.b64decode(img_bs64)
    np_image = np.frombuffer(byte_image, np.uint8)
    bgr_image = cv2.imdecode(np_image, cv2.IMREAD_COLOR)
    return bgr_image


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/read_image")
def read_image(url: str):

    # url = "https://ccc.mots.go.th/uploads/calories_img/" + file_name
    start_get = time.time()
    resp = requests.get(url)
    start = time.time()
    image = np.asarray(bytearray(resp.content), dtype="uint8")
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)

    result = reader.readtext(image)
    points = []
    for d in result:
        if ":" in d[1] or any(char.isdigit() for char in d[1]):
            points.append(
                [
                    [int(d[0][0][0]), int(d[0][0][1])],
                    [int(d[0][2][0]), int(d[0][2][1])],
                    d[1],
                ]
            )
            image = cv2.rectangle(
                image,
                [int(d[0][0][0]), int(d[0][0][1])],
                [int(d[0][2][0]), int(d[0][2][1])],
                (255, 0, 0),
                2,
            )
    _, im_arr = cv2.imencode(".jpg", image)
    im_bytes = im_arr.tobytes()
    im_b64 = base64.b64encode(im_bytes)
    end = time.time()
    return {
        "url": url,
        "time_load": start - start_get,
        "time_process": end - start,
        "result": points,
        "image": im_b64,
    }


@app.get("/check_image")
def check_image(url: str):
    start_get = time.time()
    # url = "https://ccc.mots.go.th/uploads/calories_img/" + file_name

    resp = requests.get(url)
    start = time.time()
    image = np.asarray(bytearray(resp.content), dtype="uint8")
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)

    result = reader.readtext(image)
    points = []
    for d in result:
        if ":" in d[1] or any(char.isdigit() for char in d[1]):
            points.append(
                [
                    [int(d[0][0][0]), int(d[0][0][1])],
                    [int(d[0][2][0]), int(d[0][2][1])],
                    d[1],
                ]
            )
    end = time.time()
    return {
        "url": url,
        "time_load": start - start_get,
        "time_process": end - start,
        "result": points,
    }


@app.post("/process_image")
def process_image(item: Item):

    # url = "https://ccc.mots.go.th/uploads/calories_img/cal-65ac64c0541e2.jpeg"
    start_get = time.time()
    image = base64_to_image(item.base64str)
    start = time.time()

    result = reader.readtext(image)

    points = []
    for d in result:
        x, y = (d[0][0][0] + d[0][2][0]) / 2, (d[0][0][1] + d[0][2][1]) / 2
        points.append(
            [
                [x, y],
                d,
            ]
        )
    p1 = {}
    
    for n in range(len(points)):
        if ("ม.ค." in points[n][1][1]
            or " มกราคม" in points[n][1][1]
            or "ก.พ." in points[n][1][1]
            or " กุมภาพันธ์" in points[n][1][1]
            or "มี.ค." in points[n][1][1]
            or " มีนาคม" in points[n][1][1]
            or "เม.ย." in points[n][1][1]
            or " เมษายน" in points[n][1][1]
            or "พ.ค." in points[n][1][1]
            or " พฤษภาคม" in points[n][1][1]
            or "มิ.ย." in points[n][1][1]
            or " มิถุนายน" in points[n][1][1]
            or "ก.ค." in points[n][1][1]
            or " กรกฎาคม" in points[n][1][1]
            or "ส.ค." in points[n][1][1]
            or " สิงหาคม" in points[n][1][1]
            or "ก.ย." in points[n][1][1]
            or " กันยายน" in points[n][1][1]
            or "ต.ค." in points[n][1][1]
            or " ตุลาคม" in points[n][1][1]
            or "พ.ย." in points[n][1][1]
            or " พฤศจิกายน" in points[n][1][1]
            or "ธ.ค." in points[n][1][1]
            or " ธันวาคม" in points[n][1][1]
            or " 2023" in points[n][1][1]
            or "/2023" in points[n][1][1]
            or " 2566" in points[n][1][1]
            or "/2566" in points[n][1][1]
            or " 2024" in points[n][1][1]
            or "/2024" in points[n][1][1]
            or " 2567" in points[n][1][1]
            or "/2567" in points[n][1][1]
            or " 2025" in points[n][1][1]
            or "/2025" in points[n][1][1]
            or " 2568" in points[n][1][1]
            or "/2568" in points[n][1][1]
                or "today" in points[n][1][1]):
            p1["date"] = [points[n]]
        if (
            "duration" in points[n][1][1]
            or "เวลารวม" == points[n][1][1]
            or "เวลา" == points[n][1][1]
            or "เาลา" == points[n][1][1]
            or "เวสา" == points[n][1][1]
            or " เวลา" == points[n][1][1]
            or "ระยะเวลา" == points[n][1][1]
            or "ระบะเวลา" == points[n][1][1]
            or "ระยะเาลา" == points[n][1][1]
            or " เวลาใช้งาน" == points[n][1][1]
            or "เวลาใช้งาน" == points[n][1][1]
            or " time" == points[n][1][1]
            or "workout time" == points[n][1][1]
            or "active time" in points[n][1][1]
            or "ระยะเวลาออก" in points[n][1][1]
            or "เวลาออก" in points[n][1][1]
            or "moving time" in points[n][1][1]
            or "running" in points[n][1][1]
            or "รามทั้งหมด" in points[n][1][1]
            or "ระยะเวล1ฮอกก้าลัง" in points[n][1][1]
            or "ระยะเวลา1ออกกำลังกาย" in points[n][1][1]
            or "total time" in points[n][1][1]
            or "ระยะเวลาออกกำลัง" in points[n][1][1]
            or "ระยะเวลาออกกำลังกาย" in points[n][1][1]
            or "กามอาเจลา" in points[n][1][1]
            or "เวลาราม" == points[n][1][1]
        ) \
                and not (":" in points[n][1][1]):
            p1["tm"] = [points[n]]
        if (
            "แคลอรี" == points[n][1][1]
            or "แคลอรี่ทั้งหมด" == points[n][1][1]
            or "แคลอรี่" == points[n][1][1]
            or "แคณารี" == points[n][1][1]
            or "กิโลแคล" == points[n][1][1]
            or "กิโลแคลอรี" == points[n][1][1]
            or "ศิโลแคล" == points[n][1][1]
            or "calories" in points[n][1][1]
            or "calorigs" in points[n][1][1]
            or "cal" == points[n][1][1]
            or " cal" == points[n][1][1]
            or "kcal" == points[n][1][1]
            or "พลังงานทั้งหมด" in points[n][1][1]
            or "พลังงานฮอกกำลังกาย" in points[n][1][1]
            or "พลังงานออกกำลัง" in points[n][1][1]
            or "การเผาผลาญ" in points[n][1][1]
            or "การเยาผสาเ" in points[n][1][1]
            or "เคลอรี่" == points[n][1][1]
            or "กิโลแคลอรี ทั้งหมด" == points[n][1][1]
            or "กิโฮนคลอรีทังหมค" == points[n][1][1]
            or "แคลอร์" == points[n][1][1]
            or "แคล" == points[n][1][1]
            or "พลังงานที่ใช้ไป" in points[n][1][1]
            or "กีโลแคล" in points[n][1][1]
            or "แคลอรี่ทังหมด" == points[n][1][1]
            or "พลังงานออก" in points[n][1][1]
            or "แคลอรี่รวม" in points[n][1][1]  
        ):
            p1["cal"] = [points[n]]
        if (
            "distance" in points[n][1][1]
            or "ระยะทาง" in points[n][1][1]
            or "ระปะทาง" == points[n][1][1]
            or "ระยะทางทั้งหมด" == points[n][1][1]
            or "กม." == points[n][1][1]
            or " กม." == points[n][1][1]
            or "กม" == points[n][1][1]
            or " กม" == points[n][1][1]
            or "m" == points[n][1][1]
            or " m" == points[n][1][1]
            or "km" == points[n][1][1]
            or " km" == points[n][1][1]
            or "distance(km)" == points[n][1][1]
            or "กิโลเมตร" == points[n][1][1]
            or " กิโลเมตร" == points[n][1][1]
            or "ระยะทาง(กม.)" == points[n][1][1]
            or "ระยะภางจ" == points[n][1][1]
            or "mi" == points[n][1][1]
        ) \
                and not (":" in points[n][1][1] or any(char.isdigit() for char in points[n][1][1])):
            p1["dis"] = [points[n]]
    if 'tm' in p1.keys():
        short = 1000
        for i in range(len(points)):
            if points[i] != p1["tm"][0] and ("นาที" in points[i][1][1] or ":" in points[i][1][1] or "'" in points[i][1][1]) and any(char.isdigit() for char in points[i][1][1]):
                if dist(points[i][0], p1["tm"][0][0]) < short:
                    short = dist(points[i][0], p1["tm"][0][0])
                    if len(p1["tm"]) == 1:
                        p1["tm"].append(points[i])
                    else:
                        p1["tm"][1] = points[i]
    else:
        for i in range(len(points)):
            if ":" in points[i][1][1]:
                p1["tm"] = [points[i]]
                p1["tm"].append(points[i])
    if 'cal' in p1.keys():
        short = 1000
        for i in range(len(points)):
            if points[i] != p1["cal"][0] and points[i][1][1][0].isdigit() and any(char.isdigit() for char in points[i][1][1]):
                if dist(points[i][0], p1["cal"][0][0]) < short:
                    short = dist(points[i][0], p1["cal"][0][0])
                    if len(p1["cal"]) == 1:
                        p1["cal"].append(points[i])
                    else:
                        p1["cal"][1] = points[i]
    else:
        for i in range(len(points)):
            if " kcal" in points[i][1][1]:
                p1["cal"] = [points[i]]
                p1["cal"].append(points[i])
    if 'dis' in p1.keys():
        short = 1000
        for i in range(len(points)):
            if points[i] != p1["dis"][0] and points[i][1][1][0].isdigit() and any(char.isdigit() for char in points[i][1][1]) and "'" not in points[i][1][1] and ":" not in points[i][1][1]:
                if dist(points[i][0], p1["dis"][0][0]) < short:
                    short = dist(points[i][0], p1["dis"][0][0])
                    if len(p1["dis"]) == 1:
                        p1["dis"].append(points[i])
                    else:
                        p1["dis"][1] = points[i]
    else:
        for i in range(len(points)):
            if (" km" in points[i][1][1] or "กม." in points[i][1][1] or " กม." in points[i][1][1] or "km" in points[i][1][1] or " m" in points[i][1][1] or "m" in points[i][1][1]) and not "km/h" in points[i][1][1] and not " h" in points[i][1][1] and not "meetea" in points[i][1][1]:
                p1["dis"] = [points[i]]
                p1["dis"].append(points[i])
    if "tm" in p1.keys():
        image = cv2.rectangle(
            image,
            [int(p1["tm"][1][1][0][0][0]), int(p1["tm"][1][1][0][0][1])],
            [int(p1["tm"][1][1][0][2][0]), int(p1["tm"][1][1][0][2][1])],
            (255, 0, 0),
            2,
        )
    if "cal" in p1.keys():
        image = cv2.rectangle(
            image,
            [int(p1["cal"][1][1][0][0][0]), int(p1["cal"][1][1][0][0][1])],
            [int(p1["cal"][1][1][0][2][0]), int(p1["cal"][1][1][0][2][1])],
            (255, 0, 0),
            2,
        )
    if "dis" in p1.keys():
        image = cv2.rectangle(
            image,
            [int(p1["dis"][1][1][0][0][0]), int(p1["dis"][1][1][0][0][1])],
            [int(p1["dis"][1][1][0][2][0]), int(p1["dis"][1][1][0][2][1])],
            (255, 0, 0),
            2,
        )
    if "date" in p1.keys():
        image = cv2.rectangle(
            image,
            [int(p1["date"][0][1][0][0][0]), int(p1["date"][0][1][0][0][1])],
            [int(p1["date"][0][1][0][2][0]), int(p1["date"][0][1][0][2][1])],
            (255, 0, 0),
            2,
        )
    _, im_arr = cv2.imencode(".jpg", image)
    im_bytes = im_arr.tobytes()
    im_b64 = base64.b64encode(im_bytes)
    end = time.time()
    rt = {}
    data = {}
    data["time_load"] = start - start_get
    data["time_process"] = end - start
    if "tm" in p1.keys():
        data["tm"] = p1["tm"][1][1][1]
    else:
        data["tm"] = ""
    if "cal" in p1.keys():
        data["cal"] = p1["cal"][1][1][1]
    else:
        data["cal"] = ""
    if "dis" in p1.keys():
        data["dis"] = p1["dis"][1][1][1]
    else:
        data["dis"] = ""
    if "date" in p1.keys():
        data["date"] = p1["date"][0][1][1]
    else:
        data["date"] = ""
    data["original_img"] = item.base64str
    data["process_img"] = im_b64
    rt["status"] = 200
    rt["message"] = "success"
    rt["data"] = data
    return rt
