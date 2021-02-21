# https://stackoverflow.com/a/52280812/6572046
import json
from app import app, api

app.config['SERVER_NAME'] = 'localhost'
app.app_context().__enter__()
with open('api_specification.json', 'w') as json_file:
    json.dump(api.__schema__, json_file, indent=2)
