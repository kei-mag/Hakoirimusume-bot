from time import sleep
from datetime import datetime
import io
from hakoirimusume.bme280 import BME280
from hakoirimusume.imgur import upload_as_anonymous
from picamera2 import Picamera2
import json
from flask import current_app

from linebot.v3.messaging.models import FlexMessage, FlexContainer


class ReportCreator:
    SENSOR_BUS = 1
    SENSOR_ADDR = 118

    def __init__(self, call_type=0) -> None:
        self.call_type = call_type
        # initialize camera
        try:
            self.camera = Picamera2()
            self.camera.configure("still")
        except RuntimeError:
            self.camera = None

        # initialize sensor
        try:
            self.sensor = BME280(self.SENSOR_BUS, self.SENSOR_ADDR)
        except OSError:
            self.sensor = None

        # load report template & config
        with open(f"{current_app.root_path}/resources/report_template.json", "r", encoding="utf-8") as f:
            self.report_template = json.load(f)
        self.imgur_client_id = current_app.config["IMGUR_CLIENT_ID"]

    def get_report(self) -> FlexMessage:
        report_dict = self.report_template.copy()
        cur_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        report_dict["body"]["contents"][1]["text"] = cur_time
        # Take & upload photo
        try:
            photo_bytes = self.take_photo()
            if photo_bytes is not None:
                result = upload_as_anonymous(
                    self.imgur_client_id,
                    photo_bytes,
                    name=f"rabbit-house-report_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                )
                if result is tuple:
                    # Replace photo uri
                    report_dict["hero"]["url"] = result[0]
                    report_dict["hero"]["action"]["uri"] = result[0]
                else:
                    pass
        except Exception:
            pass

        temperature = humid = pressure = "---"
        if self.sensor is not None:
            # Get Temperature, Humid & Pressure
            try:
                temperature, humid, pressure = self.sensor.read_data()
            except Exception:
                pass
        temperature = str(temperature) + " ℃"
        humid = str(humid) + " ％"
        pressure = str(pressure) + " hPa"

        # Replace sensor information
        report_dict["body"]["contents"][3]["contents"][0]["contents"][1]["text"] = temperature
        report_dict["body"]["contents"][3]["contents"][1]["contents"][1]["text"] = humid
        report_dict["body"]["contents"][3]["contents"][2]["contents"][1]["text"] = pressure

        return FlexMessage(
            altText="Rabbit's House Report", quickReply=None, contents=FlexContainer.from_dict(report_dict)
        )

    def take_photo(self):
        if self.camera is None:
            sleep(1)
            return None
        else:
            photo_data = io.BytesIO()
            self.camera.capture_file(photo_data, format="png")
            return photo_data.read()
