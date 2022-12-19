import json
import subprocess
from subprocess import PIPE

f = open("./flexmessage.json", "r")
json_data = json.load(f)
f.close()
imgur = subprocess.run("python3 ./still.py", shell=True, stdout=PIPE, stderr=PIPE, text=True)
url = imgur.stdout
url = url.replace('\n', '')
json_data['hero']["url"] = url
json_data['hero']["action"]["uri"] = url
print(json_data['footer']["contents"][0])
f = open("./flexmessage.json", "w")
f.write(json.dumps(json_data))
f.close()
