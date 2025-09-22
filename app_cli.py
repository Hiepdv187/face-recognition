import os
import sys
import json
import uuid
from database import Base, engine, SessionLocal
from models import Person
from embeddings import add_embedding
from recognition import recognize_face
import warnings
warnings.filterwarnings("ignore", category=UserWarning)
import tensorflow as tf
tf.get_logger().setLevel("ERROR")

UPLOAD_FOLDER = "dataset"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def main():
    # Đọc JSON input từ stdin
    try:
        input_data = sys.stdin.read()
        if not input_data.strip():
            print(json.dumps({"status": "error", "message": "No input data"}))
            return

        request = json.loads(input_data)

        action = request.get("action")
        name = request.get("name", "")
        image_path = request.get("image", "")

        if action == "register":
            result = register_face(name, image_path)
            print(json.dumps(result))

        elif action == "recognize":
            result = recognize_face_cli(image_path)
            print(json.dumps(result))

        else:
            print(json.dumps({"status": "error", "message": "Invalid action"}))

    except json.JSONDecodeError:
        print(json.dumps({"status": "error", "message": "Invalid JSON input"}))
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}))

def register_face(name, image_path):
    """Register face từ CLI"""
    if not name or not image_path:
        return {"status": "error", "message": "Name and image path required"}

    if not os.path.exists(image_path):
        return {"status": "error", "message": "Image file not found"}

    session = SessionLocal()
    person = session.query(Person).filter_by(name=name).first()
    if not person:
        person = Person(name=name)
        session.add(person)
        session.commit()

    filename = f"{person.id}_{uuid.uuid4().hex}.jpg"
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    # Copy file to dataset
    import shutil
    shutil.copy2(image_path, filepath)

    if not add_embedding(filepath, person.id):
        return {"status": "error", "message": "Failed to add embedding"}

    session.close()
    return {
        "status": "success",
        "message": "Face registered successfully",
        "person_id": person.id,
        "name": person.name
    }

def recognize_face_cli(image_path):
    """Recognize face từ CLI"""
    if not image_path or not os.path.exists(image_path):
        return {"status": "error", "message": "Image path required"}

    filename = f"temp_{uuid.uuid4().hex}.jpg"
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    # Copy file to dataset
    import shutil
    shutil.copy2(image_path, filepath)

    name, distance = recognize_face(filepath)

    return {
        "status": "success",
        "message": "Face recognition completed",
        "name": name,
        "distance": distance
    }

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    main()
