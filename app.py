import os

from datetime import datetime
from cs50 import SQL
from flask import Flask, flash, reidrect, render_template, request, session
from flask_session import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash


app = Flask(__name__)
