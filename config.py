
from dotenv import load_dotenv

import os

load_dotenv(override=True)

class Config:
    
    SECRET_KEY=os.getenv("SECRET_KEY", "").strip()
    
    pass