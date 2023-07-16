from os import getenv
from dotenv import load_dotenv
from typing import List
load_dotenv()
ELA_API_ORIGINS:List = getenv("ELA_API_ORIGINS","*").split()
