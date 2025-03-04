from flask import Flask, request, jsonify, render_template
from py_vapid import Vapid
from pywebpush import webpush
from base64 import urlsafe_b64encode
from cryptography.hazmat.primitives import serialization
import json

app = Flask(__name__)

# Generate VAPID keys (run once, then hardcode below)
vapid = Vapid()
vapid.generate_keys()

# Convert public key to raw bytes and then base64url encode
public_key_bytes = vapid.public_key.public_bytes(
    encoding=serialization.Encoding.X962,  # Uncompressed point format
    format=serialization.PublicFormat.UncompressedPoint
)
raw_public_key = urlsafe_b64encode(public_key_bytes).decode('utf-8').rstrip('=')
VAPID_PUBLIC_KEY = raw_public_key
VAPID_PRIVATE_KEY = vapid.private_pem().decode()

# After running once, hardcode these values and comment out the generation above
# Example:
# VAPID_PUBLIC_KEY = "BIw4Z3gKTVh9zG5gJ5gXz5xJ9T8z9xJ5gXz5xJ9T8z9xJ5gXz5xJ9T8z9xJ5gXz5xJ9T8"
# VAPID_PRIVATE_KEY = "-----BEGIN PRIVATE KEY-----\nMIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQgP8g...\n-----END PRIVATE KEY-----"

# Print for verification (remove after hardcoding)
print("Raw VAPID Public Key:", VAPID_PUBLIC_KEY)
print("VAPID Private Key:", VAPID_PRIVATE_KEY)

# Store subscriptions in memory (for demo; use a database in production)
subscriptions = []

@app.route('/')
def index():
    return render_template('index.html', vapid_public_key=VAPID_PUBLIC_KEY)

@app.route('/sw.js')
def service_worker():
    return app.send_static_file('sw.js')

@app.route('/subscribe', methods=['POST'])
def subscribe():
    subscription = request.get_json()
    print("Received subscription:", subscription)  # Debug: Verify subscription data
    subscriptions.append(subscription)
    print("Current subscriptions:", subscriptions)  # Debug: Confirm storage
    return jsonify({'status': 'success', 'message': 'Subscribed successfully'})

@app.route('/send_notification', methods=['POST'])
def send_notification():
    if not subscriptions:
        print("No subscriptions available")  # Debug: Why this fails
        return jsonify({'error': 'No subscriptions found'}), 400
    
    for subscription in subscriptions:
        try:
            print("Sending notification to:", subscription)  # Debug: Track each attempt
            webpush(
                subscription_info=subscription,
                data=json.dumps({'title': 'Test Notification', 'body': 'This is a test from Flask!'}),
                vapid_private_key=VAPID_PRIVATE_KEY,
                vapid_claims={'sub': 'mailto:example@example.com'}
            )
        except Exception as e:
            print("Notification failed:", str(e))  # Debug: Catch errors
            return jsonify({'error': str(e)}), 500
    
    return jsonify({'status': 'success', 'message': 'Notification sent'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)