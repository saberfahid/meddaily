from google_auth_oauthlib.flow import InstalledAppFlow
import pickle
import os

def complete_auth():
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    credentials_file = 'youtube_credentials.json'
    token_file = 'youtube_token.pickle'
    redirect_uri = 'http://localhost:8080/'
    
    # The URL provided by the user
    auth_response = "http://localhost:8080/?state=C6WXd3PP7PEYtuptRdHNaqQhQE5NIP&code=4/0ASc3gC0DCMsy5D8oxEMhfebonIjYYT8rF-Bcur4_34jTQVczPDdM2IwZQcjdSHT6ykMlsA&scope=https://www.googleapis.com/auth/youtube.upload"
    
    flow = InstalledAppFlow.from_client_secrets_file(
        credentials_file,
        scopes=['https://www.googleapis.com/auth/youtube.upload'],
        redirect_uri=redirect_uri
    )
    
    # Fetch token using the authorization response URL
    flow.fetch_token(authorization_response=auth_response)
    creds = flow.credentials
    
    # Save the credentials for the next run
    with open(token_file, 'wb') as token:
        pickle.dump(creds, token)
    
    print(f"✅ Credentials saved to {token_file}")
    print(f"Refresh Token: {creds.refresh_token}")

if __name__ == "__main__":
    complete_auth()
