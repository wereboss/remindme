import os
from app import create_app

app = create_app()

if __name__ == "__main__":
    # Host on 0.0.0.0 and port 9031 by default
    port = int(os.environ.get("PORT", 9031))
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug)
