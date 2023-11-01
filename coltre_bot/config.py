import os
from pathlib import Path
import configparser

def _init_ini():
    try:
        settings = configparser.ConfigParser()
        settings.read(f'{BASE_DIR}\settings.ini')
        return settings['Database']
    except KeyError:
        print('Settings file does not exist')
        # TODO
        # Возможно, стоит сделать автоматический запуск файла-конфигуратора
        exit(-1)


"""Общие переменные"""
BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
db_settings = _init_ini()

"""Переменные, связанные с ботом непосредственно"""
BOT_TOKEN = os.getenv("COLTRE_BOT_TOKEN")
COLTRE_CHANNEL_ID = os.getenv("COLTRE_CHANNEL_ID")

"""Переменные, связанные с базой данных"""
DB_HOST = db_settings['db_host']
DB_NAME = db_settings['db_name']
DB_PORT = int(db_settings['db_port'])
DB_USERNAME = db_settings['db_username']
DB_PASSWORD = db_settings['db_password']
