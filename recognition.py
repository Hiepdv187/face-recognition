import numpy as np
from deepface import DeepFace
from config import FACE_MODEL, FACE_DETECTOR, SIM_THRESHOLD
from embeddings import load_index
from database import SessionLocal
from models import Person

def recognize_face(img_path, k=1):
    try:
        print(f"🤖 Recognizing face from: {img_path}")

        reps = DeepFace.represent(
            img_path=img_path,
            model_name=FACE_MODEL,
            detector_backend=FACE_DETECTOR,
            enforce_detection=False
        )

        print(f"📊 DeepFace found {len(reps) if reps else 0} faces")

        if not reps:
            print("⚠️ No faces detected by DeepFace")
            return "NoFace", None

        query_embedding = np.array([reps[0]["embedding"]]).astype("float32")
        print(f"✅ Query embedding shape: {query_embedding.shape}")

        index, labels = load_index()
        print(f"📁 FAISS index: {'exists' if index is not None else 'None'}")
        print(f"🏷️ Labels: {'exists' if labels is not None else 'None'}")

        if index is None or labels is None:
            print("❌ FAISS index or labels missing")
            return "NoIndex", None

        print(f"🔍 Searching in index with {len(labels)} entries")
        D, I = index.search(query_embedding, k)
        distance = D[0][0]
        person_id = int(labels[I[0][0]])

        print(f"🎯 Closest match: ID={person_id}, distance={distance}")

        if distance > SIM_THRESHOLD:
            print(f"❌ Distance {distance} > threshold {SIM_THRESHOLD}, returning Unknown")
            return "Unknown", float(distance)

        session = SessionLocal()
        person = session.query(Person).filter_by(id=person_id).first()
        session.close()

        if person:
            print(f"✅ Found person: {person.name}")
            return person.name, float(distance)
        else:
            print(f"❌ Person ID {person_id} not found in database")
            return "Unknown", float(distance)

    except Exception as e:
        print(f"❌ Recognition error: {str(e)}")
        import traceback
        print("📋 Traceback:", traceback.format_exc())
        return "Error", None
