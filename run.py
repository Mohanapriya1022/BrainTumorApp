from app import create_app, db
from app.models import User

app = create_app()

def init_db():
    with app.app_context():
        db.create_all()
        print("Database tables created.")

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=8080)
