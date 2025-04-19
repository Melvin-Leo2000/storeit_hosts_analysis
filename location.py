import os
import time
import requests

class OneMapTokenManager:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.token = None
        self.expiry = 0 

    def get_token(self):

        # If no token or it's past expiry, request a new token
        if not self.token or int(time.time()) >= self.expiry:
            self._authenticate()
        return self.token

    def _authenticate(self):

        # If tokens expire, I will just re-authenticate and create new credentials again
        url = "https://www.onemap.gov.sg/api/auth/post/getToken"
        payload = {"email": self.email, "password": self.password}
        response = requests.post(url, json=payload)
        response.raise_for_status()

        data = response.json()
        self.token = data["access_token"]

        # expiry_timestamp is in UNIX time (seconds), so I'll just store directly
        self.expiry = int(data["expiry_timestamp"])

        


def get_address_from_postal(postal_code, token):

    url = f"https://www.onemap.gov.sg/api/common/elastic/search?searchVal={postal_code}&returnGeom=Y&getAddrDetails=Y&pageNum=1"
    
    # Add the Authorization header with the Bearer token
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        # Make the GET request
        response = requests.get(url, headers=headers)
        response.raise_for_status()  
        data = response.json()

        

        if "results" in data and data["results"]:
            return data["results"] 
        else:
            print("No results found for the given postal code.")
            return None
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None
    


