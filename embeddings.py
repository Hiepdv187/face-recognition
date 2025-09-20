import os
import numpy as np
import faiss
from deepface import DeepFace
from config import FACE_MODEL, FACE_DETECTOR, INDEX_PATH, LABELS_PATH, EMBEDDINGS_DIR

os.makedirs(EMBEDDINGS_DIR, exist_ok=True)

def add_embedding(img_path, person_id):
    reps = DeepFace.represent(
        img_path=img_path,
        model_name=FACE_MODEL,
        detector_backend=FACE_DETECTOR,
        enforce_detection=False
    )
    if not reps:
        print("⚠️ Không tìm thấy khuôn mặt trong ảnh")
        return False

    embedding = np.array([reps[0]["embedding"]]).astype("float32")

    # Load FAISS index
    if os.path.exists(INDEX_PATH):
        index = faiss.read_index(INDEX_PATH)
    else:
        index = faiss.IndexFlatL2(embedding.shape[1])

    # Load labels
    if os.path.exists(LABELS_PATH):
        labels = np.load(LABELS_PATH)
    else:
        labels = np.array([])

    # Add new data
    index.add(embedding)
    faiss.write_index(index, INDEX_PATH)

    labels = np.append(labels, person_id)
    np.save(LABELS_PATH, labels)

    print(f"✅ Added embedding for person {person_id}")
    return True


def load_index():
    if os.path.exists(INDEX_PATH) and os.path.exists(LABELS_PATH):
        index = faiss.read_index(INDEX_PATH)
        labels = np.load(LABELS_PATH)
        return index, labels
    return None, None
