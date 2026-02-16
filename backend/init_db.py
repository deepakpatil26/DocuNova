from app.core.database import engine, Base
from app.models.document import Document, Conversation, Message

# Create all tables
Base.metadata.create_all(bind=engine)
print("Database tables created successfully!")
