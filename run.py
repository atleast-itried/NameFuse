import os
from app.main import create_app

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 8080))
    host = os.environ.get('HOST', '0.0.0.0')
    app.run(host=host, port=port, debug=False) 