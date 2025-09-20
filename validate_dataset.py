import os
from deepface import DeepFace
from config import DATASET_DIR, FACE_MODEL

def validate_dataset():
    total, success, fail = 0, 0, 0

    for person in os.listdir(DATASET_DIR):
        person_dir = os.path.join(DATASET_DIR, person)
        if not os.path.isdir(person_dir):
            continue

        for img_name in os.listdir(person_dir):
            img_path = os.path.join(person_dir, img_name)
            total += 1
            try:
                reps = DeepFace.represent(
                    img_path=img_path,
                    model_name=FACE_MODEL,
                    detector_backend="retinaface",  # thử backend tốt hơn
                    enforce_detection=False
                )
                if isinstance(reps, list) and len(reps) > 0 and "embedding" in reps[0]:
                    success += 1
                    print(f"✅ OK: {img_path}")
                else:
                    fail += 1
                    print(f"⚠️ Fail: {img_path}")
            except Exception as e:
                fail += 1
                print(f"❌ Error {img_path}: {e}")

    print("\n📊 Report")
    print(f"Tổng số ảnh: {total}")
    print(f"Thành công: {success}")
    print(f"Lỗi: {fail}")

if __name__ == "__main__":
    validate_dataset()
