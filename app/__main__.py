import os
from app import create_app

def main():
    app = create_app()
    port = int(os.environ.get("PORT", 9031))
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    print(f"Starting RemindMe PWA on http://0.0.0.0:{port} (bound to all network interfaces)...")
    app.run(host="0.0.0.0", port=port, debug=debug)

if __name__ == "__main__":
    main()
