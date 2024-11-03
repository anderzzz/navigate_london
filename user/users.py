import os
import json

USER_ROOT_DIR = os.path.dirname(__file__)

with open(os.path.join(USER_ROOT_DIR, 'user_0.json'), 'r') as f:
    user_0 = json.load(f)
