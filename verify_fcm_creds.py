import firebase_admin
from firebase_admin import credentials, messaging
import os
import sys

def test_fcm():
    # Allow token to be passed as argument, otherwise use default
    default_token = "erQmcCBYTFCHjUkJ3QLW2S:APA91bH3mml8jrbiwVR2S_IAr_pNRRixJ-62kOzAvehZOuIJtO_uaw2jB8Ed5xkX6y2wxlrdlTzbVlvr7hUJv_lNoVqTiVz5YFpDqg3NJBn7808LZgxy4"
    
    if len(sys.argv) > 1:
        token = sys.argv[1]
    else:
        token = default_token

    with open("verify_result_explicit.txt", "w", encoding="utf-8") as f:
        def log(msg):
            print(msg)
            f.write(msg + "\n")
            f.flush()
        
        cred_path = 'serviceAccountKey.json'
        
        log(f"Checking for {cred_path}...")
        if not os.path.exists(cred_path):
            log("ERROR: serviceAccountKey.json not found!")
            return

        try:
            if not firebase_admin._apps:
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
                log("Firebase initialized.")
            else:
                 log("Firebase already initialized.")
        except Exception as e:
            log(f"ERROR Initializing Firebase: {e}")
            return

        log(f"Sending test message to token: {token[:20]}...")
        
        message = messaging.Message(
            notification=messaging.Notification(
                title="Direct Test from Antigravity",
                body="If you see this, your credentials are correct!"
            ),
            data={
                "title": "Data Test",
                "body": "Data content",
                "click_action": "FLUTTER_NOTIFICATION_CLICK"
            },
            token=token,
        )

        try:
            response = messaging.send(message)
            log(f"SUCCESS: Message sent. ID: {response}")
        except messaging.UnregisteredError:
            log("ERROR: Token is Unregistered (The app usage might be stale, or token rotated).")
        except messaging.SenderIdMismatchError:
            log("ERROR: Sender ID Mismatch (Project ID in Json doesn't match the app that gen the token).")
        except Exception as e:
            log(f"ERROR Sending: {e}")

if __name__ == "__main__":
    test_fcm()
