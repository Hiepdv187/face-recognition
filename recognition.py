import numpy as np
from deepface import DeepFace
from config import FACE_MODEL, FACE_DETECTOR, SIM_THRESHOLD
from embeddings import load_index
from database import SessionLocal
from models import Person

def recognize_face(img_path, k=1):
    reps = DeepFace.represent(
        img_path=img_path,
        model_name=FACE_MODEL,
        detector_backend=FACE_DETECTOR,
        enforce_detection=False
    )
    if not reps:
        return "NoFace", None

    query_embedding = np.array([reps[0]["embedding"]]).astype("float32")

    index, labels = load_index()
    if index is None:
        return "NoIndex", None

    D, I = index.search(query_embedding, k)
    distance = D[0][0]
    person_id = int(labels[I[0][0]])

    if distance > SIM_THRESHOLD:
        return "Unknown", float(distance)

    session = SessionLocal()
    person = session.query(Person).filter_by(id=person_id).first()
    return person.name if person else "Unknown", float(distance)
