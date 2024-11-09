from flask import Flask
from pymongo import MongoClient
from flask_pymongo import PyMongo

with open("mongoURI.txt", "r") as file:
    mongoURI = file.readline().strip()


def create_app():
    app = Flask(__name__)
    app.config["MONGO_URI"] = mongoURI
    return app


def createMongoDB(app):
    mongoClient = MongoClient(mongoURI)
    mongo = PyMongo(app)
    return mongo
