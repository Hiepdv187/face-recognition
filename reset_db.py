import os
import shutil
from database import Base, engine, SessionLocal
from models import Person

DATASET_FOLDER = "dataset"
INDEX_FILE = "face_index.faiss"
LABELS_FILE = "face_labels.npy"

def reset():
    # Xoá database cũ
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    session.query(Person).delete()
    session.commit()
    session.close()
    print("✅ Database đã reset")

    # Xoá embeddings FAISS
    if os.path.exists(INDEX_FILE):
        os.remove(INDEX_FILE)
        print("✅ Xoá FAISS index")
    if os.path.exists(LABELS_FILE):
        os.remove(LABELS_FILE)
        print("✅ Xoá labels file")

    # Xoá dataset (ảnh cũ)
    if os.path.exists(DATASET_FOLDER):
        shutil.rmtree(DATASET_FOLDER)
        print("✅ Xoá dataset folder")
    os.makedirs(DATASET_FOLDER, exist_ok=True)

if __name__ == "__main__":
    reset()
