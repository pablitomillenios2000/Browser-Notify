from flask import Flask, request, jsonify, render_template
import json
from py_vapid import Vapid
from pywebpush import webpush
import os

app = Flask(__name__)

# Generate VAPID keys (run once, then hardcode them)
# vapid = Vapid()
# vapid.generate_keys()
# VAPID_PRIVATE_KEY = vapid.private_pem().decode()
# VAPID_PUBLIC_KEY = vapid.public_pem().decode()

# Hardcode these after generating (replace placeholders)
VAPID_PUBLIC_KEY = "MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAExiMZoqcjIFPe9dM6BMrOUp/VTwiPs7sCT6legmKHgcJ2q9lakXI29Gtt52DsaIA1laGGJrPf9pWbpjfN6tJAPw=="
VAPID_PRIVATE_KEY = "MIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQgvz5lgO5EwvyR+fNIkmewXCnvihsolGMAMYvtJOHuOHyhRANCAATGIxmipyMgU9710zoEys5Sn9VPCI+zuwJPqV6CYoeBwnar2VqRcjb0a23nYOxogDWVoYYms9/2lZumN83q0kA/"

# Store subscriptions (in-memory for demo; use a database in production)
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
    subscriptions.append(subscription)
    return jsonify({'status': 'success', 'message': 'Subscribed successfully'})

@app.route('/send_notification', methods=['POST'])
def send_notification():
    if not subscriptions:
        return jsonify({'error': 'No subscriptions found'}), 400
    
    for subscription in subscriptions:
        try:
            webpush(
                subscription_info=subscription,
                data=json.dumps({'title': 'Test Notification', 'body': 'This is a test from Flask!'}),
                vapid_private_key=VAPID_PRIVATE_KEY,
                vapid_claims={'sub': 'mailto:example@example.com'}
            )
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return jsonify({'status': 'success', 'message': 'Notification sent'})

if __name__ == '__main__':
    # Print VAPID keys on first run, then hardcode them above
    print("VAPID Public Key:", VAPID_PUBLIC_KEY)
    print("VAPID Private Key:", VAPID_PRIVATE_KEY)
    app.run(debug=True, port=5000)