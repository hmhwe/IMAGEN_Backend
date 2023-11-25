import os
from dotenv import load_dotenv

load_dotenv()

PICAS_HOST_URL="https://picas.grid.sara.nl:6984/"
PICAS_DATABASE="imagen"
PICAS_USERNAME= os.getenv("PICAS_USERNAME")
PICAS_PASSWORD=os.getenv("PICAS_PASSWORD")
