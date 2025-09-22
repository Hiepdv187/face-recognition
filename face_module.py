"""
Face Recognition Module for Golang Integration
Export functions để Golang có thể gọi trực tiếp
"""

import os
import uuid
import warnings
warnings.filterwarnings("ignore", category=UserWarning)
import tensorflow as tf
tf.get_logger().setLevel("ERROR")

# Import các module cần thiết
from database import SessionLocal
from models import Person
from embeddings import add_embedding
from recognition import recognize_face

UPLOAD_FOLDER = "dataset"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def register_face(name: str, image_path: str) -> dict:
    """
    Register a new face
    Args:
        name: Person name
        image_path: Path to image file
    Returns:
        dict: Registration result
    """
    if not name or not image_path:
        return {"status": "error", "message": "Name and image path required"}

    if not os.path.exists(image_path):
        return {"status": "error", "message": "Image file not found"}

    session = SessionLocal()

    try:
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

        return {
            "status": "success",
            "message": "Face registered successfully",
            "person_id": person.id,
            "name": person.name
        }
    finally:
        session.close()

def recognize_face_func(image_path: str) -> dict:
    """
    Recognize face from image
    Args:
        image_path: Path to image file
    Returns:
        dict: Recognition result
    """
    if not image_path or not os.path.exists(image_path):
        return {"status": "error", "message": "Image path required"}

    filename = f"temp_{uuid.uuid4().hex}.jpg"
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    try:
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
    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_all_persons() -> dict:
    """
    Get all registered persons
    Returns:
        dict: List of all persons
    """
    session = SessionLocal()

    try:
        persons = session.query(Person).all()
        result = []
        for person in persons:
            result.append({
                "id": person.id,
                "name": person.name
            })
        return {"status": "success", "persons": result}
    finally:
        session.close()

def delete_person(person_id: int) -> dict:
    """
    Delete a person by ID
    Args:
        person_id: Person ID to delete
    Returns:
        dict: Deletion result
    """
    session = SessionLocal()

    try:
        person = session.query(Person).filter_by(id=person_id).first()
        if not person:
            return {"status": "error", "message": "Person not found"}

        session.delete(person)
        session.commit()

        return {"status": "success", "message": "Person deleted successfully"}
    finally:
        session.close()
