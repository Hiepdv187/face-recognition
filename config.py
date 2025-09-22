import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# DeepFace config
FACE_MODEL = "ArcFace"
FACE_DETECTOR = "retinaface"

# FAISS + labels
EMBEDDINGS_DIR = os.path.join(BASE_DIR, "embeddings")
INDEX_PATH = os.path.join(EMBEDDINGS_DIR, "face_index.faiss")
LABELS_PATH = os.path.join(EMBEDDINGS_DIR, "labels.npy")

# DB config - Support both SQLite and PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'face_recognition.db')}")
SQLALCHEMY_DATABASE_URL = DATABASE_URL

# Threshold cho Unknown
SIM_THRESHOLD = 0.5

# Upload folder
UPLOAD_FOLDER = os.path.join(BASE_DIR, "dataset")
