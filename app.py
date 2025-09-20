import os
import uuid
import json
from flask import Flask, request, jsonify, render_template, Response
from database import Base, engine, SessionLocal
from models import Person
from embeddings import add_embedding
from recognition import recognize_face
from flask_cors import CORS
import warnings
warnings.filterwarnings("ignore", category=UserWarning)
import tensorflow as tf
tf.get_logger().setLevel("ERROR")

UPLOAD_FOLDER = "dataset"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False
CORS(app)

Base.metadata.create_all(bind=engine)
@app.route("/")
def index():
    return render_template("test.html")

@app.route("/face-register", methods=["POST"])
def register():
    name = request.form.get("name")
    file = request.files.get("file")

    if not name or not file:
        return Response(
            json.dumps({"error": "Thiếu tên hoặc ảnh"}, ensure_ascii=False),
            content_type="application/json; charset=utf-8",
            status=400
        )

    session = SessionLocal()
    person = session.query(Person).filter_by(name=name).first()
    if not person:
        # Nếu chưa có thì tạo mới
        person = Person(name=name)
        session.add(person)
        session.commit()

    # Luôn cho phép thêm ảnh mới
    filename = f"{person.id}_{uuid.uuid4().hex}.jpg"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    # Thêm embedding
    if not add_embedding(filepath, person.id):
        return Response(
            json.dumps({"error": "Không thêm được embedding"}, ensure_ascii=False),
            content_type="application/json; charset=utf-8",
            status=500
        )

    response = {
        "message": "Đăng ký thành công",
        "person_id": person.id,
        "name": person.name,   # trả lại đầy đủ tên
        "file": filename
    }
    return Response(
        json.dumps(response, ensure_ascii=False),
        content_type="application/json; charset=utf-8",
        status=200
    )

@app.route("/face-recognition", methods=["POST"])
def recognize():
    file = request.files.get("file")
    if not file:
        return Response(
            json.dumps({"error": "Thiếu ảnh"}, ensure_ascii=False),
            content_type="application/json; charset=utf-8",
            status=400
        )

    filename = f"temp_{uuid.uuid4().hex}.jpg"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    name, distance = recognize_face(filepath)

    response = {
        "status": "success",
        "name": name,           # họ tên đầy đủ
        "distance": distance,
        "file": filename        # ảnh đã upload
    }
    return Response(
        json.dumps(response, ensure_ascii=False),
        content_type="application/json; charset=utf-8",
        status=200
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
