import os

BOT_TOKEN = os.getenv("COLTRE_BOT_TOKEN")
COLTRE_CHANNEL_ID = os.getenv("COLTRE_CHANNEL_ID")

DB_HOST = os.getenv("COLTRE_DB_HOST") if os.getenv("COLTRE_DB_HOST") else "localhost"
DB_NAME = os.getenv("COLTRE_DB_NAME") if os.getenv("COLTRE_DB_NAME") else "coltre"
DB_PORT = int(3307)
DB_USERNAME = os.getenv("COLTRE_DB_USERNAME") if os.getenv("COLTRE_DB_USERNAME") else "bot"
DB_PASSWORD = os.getenv("COLTRE_DB_PASSWORD") if os.getenv("COLTRE_DB_PASSWORD") else "sOSDGB"
