import os
from pprint import pprint

import yaml

os.chdir(os.path.dirname(__file__))
with open("../instance/hakoirimusume.yml") as file:
    data = yaml.safe_load(file)
    pprint(data)