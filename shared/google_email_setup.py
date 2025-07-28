from google_apis_start import create_service

### (1)
### THIS FILE IS CONNECTED TO google_apis_start.py
### (maybe I can make this the main function for google_apis_start.py?)
### NEED TO RUN THIS FIRST IN ORDER TO USE THE GOOGLE API FUNCTIONS
client_secret_file = 'client_secret.json'
api_name = 'gmail'
api_version = 'v1'
scopes = ['https://mail.google.com/']
service = create_service(client_secret_file, api_name, api_version, scopes)

# dir(service) # allows you to see the users?