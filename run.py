from app import create_app

print("[DEBUG] Starting application…")

app = create_app()
print("[DEBUG] Flask app created successfully")

if __name__ == "__main__":
    print("[DEBUG] __main__ triggered → running app on host=0.0.0.0, port=8080, debug=True")
    app.run(host="0.0.0.0", port=8080, debug=True)
    # Note: In production, use a WSGI server like Gunicorn to run the app