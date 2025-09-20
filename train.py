import os
from database import init_db, SessionLocal, Person
from embeddings import build_embeddings
from config import DATASET_DIR

def load_dataset_to_db():
    session = SessionLocal()
    for idx, folder in enumerate(os.listdir(DATASET_DIR), start=1):
        if not session.query(Person).filter_by(folder=folder).first():
            person = Person(id=idx, name=folder, folder=folder)
            session.add(person)
    session.commit()

if __name__ == "__main__":
    init_db()
    load_dataset_to_db()
    build_embeddings()
