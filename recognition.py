import numpy as np
from deepface import DeepFace
from config import FACE_MODEL, FACE_DETECTOR, SIM_THRESHOLD
from embeddings import load_index
from database import SessionLocal
from models import Person

def recognize_face(img_path, k=1, resize_to=None):
    """
    Fast + accurate recognition flow:
    - If resize_to is provided, run face detection on a downscaled copy to save time.
    - Map the detected bbox back to the original image coordinates.
    - Crop the original image to that bbox and compute embedding on the crop for best accuracy.
    - Search FAISS index and return (name, distance) or ("Unknown", distance).
    """
    tmp_resized = None
    face_crop_path = None
    try:
        print(f"🤖 Recognizing face from: {img_path}")

        # Load original image to get size
        from PIL import Image
        import os, uuid

        orig_img = Image.open(img_path).convert('RGB')
        orig_w, orig_h = orig_img.size

        detect_path = img_path

        # If requested, create a small resized image for faster face detection only
        if resize_to:
            try:
                small = orig_img.resize((int(resize_to[0]), int(resize_to[1])), Image.LANCZOS)
                tmp_resized = os.path.join(os.path.dirname(img_path), f"tmp_resize_{uuid.uuid4().hex}.jpg")
                small.save(tmp_resized)
                detect_path = tmp_resized
                print(f"🔧 Using resized image for detection: {tmp_resized}")
            except Exception as e:
                print(f"⚠️ Failed to create resized image for detection: {e}. Falling back to original for detection.")

        # Use DeepFace (detector only) to detect faces on detect_path
        reps = DeepFace.represent(
            img_path=detect_path,
            model_name=FACE_MODEL,
            detector_backend=FACE_DETECTOR,
            enforce_detection=False
        )

        print(f"📊 DeepFace detection returned {len(reps) if reps else 0} face representations")

        if not reps:
            print("⚠️ No faces detected by DeepFace")
            return "NoFace", None

        # DeepFace.represent returns embedding for the face detected on the image we passed (detect_path).
        # If we used a resized image for detection, try to obtain the bounding box from the result
        # and map it back to the original image, then crop the original and compute embedding on the crop.
        detection = reps[0].get('facial_area') if isinstance(reps[0], dict) else None

        if detection and tmp_resized:
            # facial_area format: (x, y, w, h) or dict depending on backend; try tuple/list first
            try:
                if isinstance(detection, (list, tuple)) and len(detection) == 4:
                    dx, dy, dw, dh = detection
                elif isinstance(detection, dict) and {'x','y','w','h'}.issubset(detection.keys()):
                    dx = detection['x']; dy = detection['y']; dw = detection['w']; dh = detection['h']
                else:
                    # Unknown format - fall back to using embedding from detect_path
                    dx = dy = dw = dh = None
            except Exception:
                dx = dy = dw = dh = None

            if dx is not None:
                # Map coordinates from resized image space back to original
                small_w, small_h = Image.open(detect_path).size
                x_scale = orig_w / float(small_w)
                y_scale = orig_h / float(small_h)

                left = int(max(0, dx * x_scale))
                top = int(max(0, dy * y_scale))
                right = int(min(orig_w, (dx + dw) * x_scale))
                bottom = int(min(orig_h, (dy + dh) * y_scale))

                # Expand bbox slightly to include context
                pad_w = int((right - left) * 0.15)
                pad_h = int((bottom - top) * 0.15)
                left = max(0, left - pad_w)
                top = max(0, top - pad_h)
                right = min(orig_w, right + pad_w)
                bottom = min(orig_h, bottom + pad_h)

                try:
                    crop = orig_img.crop((left, top, right, bottom))
                    face_crop_path = os.path.join(os.path.dirname(img_path), f"tmp_crop_{uuid.uuid4().hex}.jpg")
                    crop.save(face_crop_path)
                    print(f"✂️ Saved face crop for embedding: {face_crop_path}")
                except Exception as e:
                    print(f"⚠️ Failed to crop original image: {e}. Will use detected embedding from resized image.")

        # If we produced a face crop, compute embedding on the crop for best accuracy; otherwise use reps[0]
        if face_crop_path:
            try:
                reps_crop = DeepFace.represent(
                    img_path=face_crop_path,
                    model_name=FACE_MODEL,
                    detector_backend=FACE_DETECTOR,
                    enforce_detection=False
                )
                if reps_crop and isinstance(reps_crop, list) and 'embedding' in reps_crop[0]:
                    query_embedding = np.array([reps_crop[0]['embedding']]).astype('float32')
                else:
                    # fallback to original reps
                    query_embedding = np.array([reps[0]['embedding']]).astype('float32')
            except Exception as e:
                print(f"⚠️ Failed to compute embedding on crop: {e}. Falling back to detected embedding.")
                query_embedding = np.array([reps[0]['embedding']]).astype('float32')
        else:
            # No crop available; use embedding from detection step
            try:
                query_embedding = np.array([reps[0]['embedding']]).astype('float32')
            except Exception:
                print("❌ No embedding available from detection result")
                return "Error", None

        print(f"✅ Query embedding shape: {query_embedding.shape}")

        # Normalize query embedding to unit length for consistent similarity
        try:
            qnorm = np.linalg.norm(query_embedding, axis=1, keepdims=True)
            qnorm[qnorm == 0] = 1.0
            query_embedding = query_embedding / qnorm
        except Exception:
            pass

        index, labels = load_index()
        print(f"📁 FAISS index: {'exists' if index is not None else 'None'}")
        print(f"🏷️ Labels: {'exists' if labels is not None else 'None'}")

        if index is None or labels is None:
            print("❌ FAISS index or labels missing")
            return "NoIndex", None

        print(f"🔍 Searching in index with {len(labels)} entries")
        D, I = index.search(query_embedding, k)
        distance = float(D[0][0])
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
    finally:
        # clean up temp images if created
        try:
            if tmp_resized and os.path.exists(tmp_resized):
                os.remove(tmp_resized)
                print(f"🧹 Removed temp resized image: {tmp_resized}")
        except Exception:
            pass
        try:
            if face_crop_path and os.path.exists(face_crop_path):
                os.remove(face_crop_path)
                print(f"🧹 Removed temp crop image: {face_crop_path}")
        except Exception:
            pass
