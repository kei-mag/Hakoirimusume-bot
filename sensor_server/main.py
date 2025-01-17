import datetime
import http.server
import json
import os
import re
from urllib.parse import parse_qs, urlparse

import imgur

try:
    import tomllib
except ImportError:
    import tomli as tomllib  # If you run this script on Python 3.10 or earlier, please install `tomllib` via pip.

CONFIG_FILE = "./config.toml"
DASHBOARD_HTML_FILE = "templates/dashboard.html"
SHUTTING_DOWN_HTML_FILE = "templates/shutting_down.html"
RELOAD_INTERVAL = 600  # sec.
ACCEPT_ADDR = "0.0.0.0"
ENV_VAL_FORM = re.compile(r"\${(.+)}")

# ----- Default config values -----
port = 80
imgur_client_id = ""
enable_camera = False
i2c_bus = 1
i2c_addr = 0x76
sensor_data_file = "./sensor_data.csv"
log_level = "ALL"
# ---------------------------------

dashboard_html = """
<!DOCTYPE HTML>
<html lang="en">
<head>
<title>Hakoirimusume Sensor Server</title>
<body>
<h1>Dashboard is unavailable</h1>
<p>Sensor Dashboard is not currently available</p>
<p>Please check the status of server applications.</p>
</body>
</html>
"""
shutting_down_html = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta http-equiv="refresh" content="10;URL=/">
    <meta charset="UTF-8">
    <title>シャットダウン中</title>
</head>
<body>
        <h1>サーバーをシャットダウンしています</h1>
                <p>シャットダウンには30秒ほどかかります。本体のLEDが消灯するまで電源コードを抜かないでください。</p>
                
            </body>
            </html>
"""
camera = None
bme280 = None


def main():
    global camera, bme280, dashboard_html
    os.chdir(os.path.dirname(__file__))
    print("Hakoirimusume Sensor Server")
    load_config()
    print("----- Running Info -----")
    print(f"Working directory: {os.getcwd()}")
    print(f"Loaded config file: {os.path.abspath(CONFIG_FILE)}")
    print(f"Listening PORT: {port}")
    print(f"Imgur Client ID: {imgur_client_id}")
    print(f"Enable Camera: {enable_camera}")
    print(f"BME280 I2C-BUS: {i2c_bus}")
    print(f"BME280 I2C-ADDR: 0x{i2c_addr:x}")
    print(f"Sensor Data File: {sensor_data_file}")
    print("------------------------")
    try:
        from bme280 import BME280
        bme280 = BME280(i2c_bus, i2c_addr)
    except Exception as e:
        print("Error has occurred while initializing BME280. Continue without BME 280: ", e)
    if enable_camera:
        try:
            from picamera import PiCamera
            camera = PiCamera()
        except Exception as e:
            print("Error has occurred while initializing PiCamera. Continue without PiCamera: ", e)
    try:
        with open(DASHBOARD_HTML_FILE, "r", encoding="UTF-8") as file:
            dashboard_html = file.read()
            dashboard_html = dashboard_html.replace("{{INTERVAL}}", str(RELOAD_INTERVAL))
    except Exception as e:
        print("Error has occurred while reading dashboard.html, dashboard is not available: ", e)
    with http.server.HTTPServer((ACCEPT_ADDR, port), CustomHTTPRequestHandler) as httpd:
        print("serving at port", port)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
    print("Stopped server.")


def dict_get(d, key, default=None):
    """ Get value from dictionary with dot-separated key
    :param d: Dictionary to be searched
    :param key: Target key (dot-separated format is available, e.g. "key1.key2.key3")
    :param default: Default value if the key is not found
    :return: Value of the key
    """
    keys = key.split(".")
    for k in keys:
        if k in d:
            d = d[k]
        else:
            return default
    return d


def load_config():
    global port, imgur_client_id, enable_camera, i2c_bus, i2c_addr, sensor_data_file, log_level
    config = tomllib.load(open(CONFIG_FILE, mode="rb"))
    port = replace_env(dict_get(config, "server.port", port))
    imgur_client_id = replace_env(dict_get(config, "imgur.client-id", imgur_client_id))
    enable_camera = dict_get(config, "hardware.pi-camera", enable_camera)
    i2c_bus = dict_get(config, "hardware.bme280.i2c-bus", i2c_bus)
    i2c_addr = dict_get(config, "hardware.bme280.i2c-address", i2c_addr)
    sensor_data_file = replace_env(dict_get(config, "datalog.filepath", sensor_data_file))
    log_level = dict_get(config, "datalog.level", log_level)
    cwd = os.getcwd()
    os.chdir(os.path.dirname(CONFIG_FILE))
    sensor_data_file = os.path.abspath(sensor_data_file)
    os.chdir(cwd)


def replace_env(value):
    if isinstance(value, str):
        match = ENV_VAL_FORM.search(value)
        if match:
            return ENV_VAL_FORM.sub(os.getenv(match.group(1), ""), value)
    return value


def get_current_iso_timestamp(cur_time=datetime.datetime.now()):
    # Calculate offset time without pytz package
    offset = cur_time.replace(tzinfo=datetime.UTC) - datetime.datetime.now(datetime.UTC)
    total_seconds = offset.total_seconds()
    hours, remainder = divmod(total_seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    offset_str = "{:+03d}:{:02d}".format(int(hours), int(minutes))
    timestamp_iso = cur_time.replace(microsecond=0).isoformat() + offset_str
    return timestamp_iso


def write_log(timestamp, temp, hum, press, image_url=None, deletehash=None):
    with open(sensor_data_file, "a") as file:
        file.write(f"{timestamp},{temp},{hum},{press},{image_url},{deletehash}\n")


class CustomHTTPRequestHandler(http.server.BaseHTTPRequestHandler):

    def _send_response(self, content, content_type="text/html"):
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.end_headers()
        self.wfile.write(content.encode())

    def do_GET(self):
        self.log_message("%s", self.headers)
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query = parse_qs(parsed_path.query, keep_blank_values=True)
        if path == "/":
            temp = press = humid = "---"
            if bme280:
                try:
                    temp, press, humid = bme280.read_data()
                    if log_level == "ALL":
                        write_log(get_current_iso_timestamp(), temp, humid, press)
                except Exception as e:
                    print("Failed to get BME280 data: ", e)
                else:
                    temp = f"{temp:.1f}"
                    humid = f"{humid:.1f}"
                    press = f"{press:.0f}"
            cur_time = datetime.datetime.now()
            content = dashboard_html
            content = content.replace("{{DATETIME}}", cur_time.strftime("%Y/%m/%d %H:%M:%S"))
            content = content.replace("{{TEMP}}", temp)
            content = content.replace("{{HUMID}}", humid)
            content = content.replace("{{PRESS}}", press)
            self._send_response(content)
        elif path == "/get":
            temp = press = humid = None
            if bme280:
                try:
                    temp, press, humid = bme280.read_data()
                except Exception as e:
                    print("Failed to get BME280 data: ", e)
            cur_time = datetime.datetime.now()
            cur_timestamp = get_current_iso_timestamp(cur_time)
            content = {"time": cur_timestamp}
            content["temp"] = temp
            content["humid"] = humid
            content["press"] = press
            if "withcamera" in query:
                content["photo"] = None
                content["deletehash"] = None
                if camera:
                    try:
                        try:
                            image = camera.capture_bytes()
                        except Exception as e:
                            print("Failed to capture image: ", e)
                        else:
                            if temp is None or humid is None or press is None:
                                description = "Sensor data is not available."
                            else:
                                description = f"Temperature: {temp:.1f}, Humidity: {humid:.1f}%, Pressure: {press:.1f}hPa"
                            ret = imgur.upload_as_anonymous(imgur_client_id, image,
                                                            capture_datetime=cur_time.strftime("%Y/%m%d %H:%M:%S"),
                                                            description=description)
                            if len(ret) == 2:
                                content["photo"], content["deletehash"] = ret
                            else:
                                print("Failed to upload image to Imgur: ", ret)
                    except Exception as e:
                        print("Failed to get PiCamera data: ", e)
                    write_log(cur_timestamp, temp, humid, press, content["photo"], content["deletehash"])
                else:
                    write_log(cur_timestamp, temp, humid, press)
            else:
                if log_level == "ALL":
                    write_log(cur_timestamp, temp, humid, press)
            self._send_response(json.dumps(content), content_type="application/json")
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        self.log_message("%s", self.headers)
        if self.path == "/":
            content = """
            <!DOCTYPE html>
            <html lang="ja">
            <head>
                <meta http-equiv="refresh" content="10;URL=/">
                <meta charset="UTF-8">
                <title>シャットダウン中</title>
            </head>
            <body>
                <h1>サーバーをシャットダウンしています</h1>
                <p>シャットダウンには30秒ほどかかります。本体のLEDが消灯するまで電源コードを抜かないでください。</p>
                
            </body>
            </html>
            """
            # シャットダウンの処理
            self._send_response(content)
            os.system("sudo shutdown -h now")
        else:
            self.send_response(404)
            self.end_headers()


if __name__ == "__main__":
    main()
