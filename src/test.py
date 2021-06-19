from rpiSS import SoftwareSerial

from flask import Flask
from flask import request

import random
import threading


class App(Flask)

    def __init__(self):

        super(App, self).__init__()