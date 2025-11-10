from dotenv import dotenv_values
from aiogram import Bot

ENV = dotenv_values(".env")

Token = ENV["TOKEN"]
ADMIN = ENV["ADMIN"]
ADMIN1 = ENV["ADMIN1"]
API = ENV["API"]

bot = Bot(token=Token)