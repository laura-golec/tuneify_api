from dotenv import load_dotenv
import os

load_dotenv()

API_KEYS = os.getenv('API_KEYS')
ROOT_DIR = os.getenv('ROOT_DIR')
TEMP_DIR = os.getenv('TEMP_DIR')
SUDO_PASSWORD = os.getenv('SUDO_PASSWORD')
USER = os.getenv('USER')
RIP_SETTINGS = os.getenv('RIP_SETTINGS')
RIP_SETTINGS_RULES = os.getenv('RIP_SETTINGS_RULES')