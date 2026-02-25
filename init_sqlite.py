from apps.api.app.database import engine, Base
from apps.api.app import models

print("Creating SQLite tables...")
Base.metadata.create_all(bind=engine)
print("Tables created successfully.")
