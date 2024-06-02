import os

def add_default_database():
    from superset import app
    from superset.models.core import Database
    from superset.extensions import db

    app.app_context().push()    

    with app.app_context():
        engine_uri = f'postgresql://{os.getenv("DB_USER", "defaultuser")}:{os.getenv("DB_PASS", "defaultpassword")}@{os.getenv("DB_HOST", "localhost")}:{os.getenv("DB_PORT", "5432")}/{os.getenv("DB_NAME", "defaultdb")}'
        if not db.session.query(Database).filter_by(sqlalchemy_uri=engine_uri).first():
            db_conn = Database(
                database_name='Default PostgreSQL',
                sqlalchemy_uri=engine_uri,
            )
            db.session.add(db_conn)
            db.session.commit()
            print("Default database added.")
        else:
            print("Database already configured.")

if __name__ == "__main__":
    add_default_database()