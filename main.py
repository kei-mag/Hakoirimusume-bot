"""LINE BOT "Hakoirimusume" server program

Please run this program after running "install.py"

Copyright (c) 2023 Keisuke Magara
"""

# ###################### NOTICE ########################
# This is development code.
# Do not use frontend.app.run() in production code.
# ######################################################

import os

import model.frontend as frontend

print("Launched Hakoirimusume server.")
print("Initializing...")
# Change working directory to here.
default_working_dir = os.getcwd()
os.chdir(os.path.abspath(__file__))
frontend.app.run()
