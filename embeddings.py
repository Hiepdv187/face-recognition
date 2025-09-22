import os
import numpy as np
import faiss
from deepface import DeepFace
from config import FACE_MODEL, FACE_DETECTOR, INDEX_PATH, LABELS_PATH, EMBEDDINGS_DIR

os.makedirs(EMBEDDINGS_DIR, exist_ok=True)

def add_embedding(img_path, person_id):
    try:
        # First attempt to detect and get facial_area
        reps = DeepFace.represent(
            img_path=img_path,
            model_name=FACE_MODEL,
            detector_backend=FACE_DETECTOR,
            enforce_detection=False
        )
    except Exception as e:
        print(f"⚠️ DeepFace.represent error during add_embedding: {e}")
        reps = None

    if not reps:
        print("Warning: no face found in image (initial detect)")
        return False

    # If facial_area info exists, crop original image and compute embedding on the crop
    embedding = None
    facial_area = reps[0].get('facial_area') if isinstance(reps[0], dict) else None
    if facial_area:
        try:
            from PIL import Image
            import uuid
            orig = Image.open(img_path).convert('RGB')
            # facial_area may be tuple (x,y,w,h) or dict
            if isinstance(facial_area, (list, tuple)) and len(facial_area) == 4:
                x, y, w, h = facial_area
            elif isinstance(facial_area, dict) and {'x','y','w','h'}.issubset(facial_area.keys()):
                x = facial_area['x']; y = facial_area['y']; w = facial_area['w']; h = facial_area['h']
            else:
                x = y = w = h = None

            if x is not None:
                left = int(max(0, x))
                top = int(max(0, y))
                right = int(min(orig.width, x + w))
                bottom = int(min(orig.height, y + h))
                pad_w = int((right - left) * 0.15)
                pad_h = int((bottom - top) * 0.15)
                left = max(0, left - pad_w)
                top = max(0, top - pad_h)
                right = min(orig.width, right + pad_w)
                bottom = min(orig.height, bottom + pad_h)

                crop = orig.crop((left, top, right, bottom))
                tmp_crop = os.path.join(os.path.dirname(img_path), f"tmp_regcrop_{uuid.uuid4().hex}.jpg")
                crop.save(tmp_crop)
                reps_crop = DeepFace.represent(
                    img_path=tmp_crop,
                    model_name=FACE_MODEL,
                    detector_backend=FACE_DETECTOR,
                    enforce_detection=False
                )
                if reps_crop and isinstance(reps_crop, list) and 'embedding' in reps_crop[0]:
                    embedding = np.array([reps_crop[0]['embedding']]).astype('float32')
                try:
                    if os.path.exists(tmp_crop):
                        os.remove(tmp_crop)
                except Exception:
                    pass
        except Exception as e:
            print(f"Warning: failed to crop and compute embedding on crop during register: {e}")

    # Fallback to using embedding from initial represent if crop-based embedding isn't available
    if embedding is None:
        try:
            embedding = np.array([reps[0]["embedding"]]).astype("float32")
        except Exception:
            print("⚠️ No embedding available to add")
            return False

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

    # Normalize embedding to unit length (recommended for ArcFace / cosine similarity)
    try:
        norm = np.linalg.norm(embedding, axis=1, keepdims=True)
        norm[norm == 0] = 1.0
        embedding = embedding / norm
    except Exception:
        pass

    # Add new data
    index.add(embedding)
    faiss.write_index(index, INDEX_PATH)

    labels = np.append(labels, person_id)
    # Ensure integer dtype for labels
    try:
        labels = np.array(labels, dtype=np.int64)
    except Exception:
        pass
    np.save(LABELS_PATH, labels)

    print(f"Added embedding for person {person_id}")
    return True


def load_index():
    if os.path.exists(INDEX_PATH) and os.path.exists(LABELS_PATH):
        index = faiss.read_index(INDEX_PATH)
        labels = np.load(LABELS_PATH)
        return index, labels
    return None, None


def rebuild_index_from_dataset(dataset_dir=None):
    """
    Rebuild FAISS index from all images in dataset_dir.
    Filenames must start with '<person_id>_' so we can extract labels.
    This rebuild will overwrite existing index and labels file.
    """
    dataset_dir = dataset_dir or os.path.join(os.path.dirname(INDEX_PATH), '..', 'dataset')
    dataset_dir = os.path.abspath(dataset_dir)
    print(f"Rebuilding FAISS index from dataset: {dataset_dir}")

    files = []
    try:
        for fname in os.listdir(dataset_dir):
            if fname.lower().endswith(('.jpg', '.jpeg', '.png')) and '_' in fname:
                files.append(os.path.join(dataset_dir, fname))
    except Exception as e:
        print(f"Failed to list dataset dir: {e}")
        return 0

    if not files:
        print("No dataset files found to rebuild index")
        return 0

    embeddings_list = []
    labels_list = []

    for fpath in files:
        try:
            fname = os.path.basename(fpath)
            pid_str = fname.split('_', 1)[0]
            person_id = int(pid_str)
        except Exception:
            print(f"Skipping file with invalid prefix (no person id): {fname}")
            continue

        # Try to compute embedding similarly to add_embedding (crop if possible)
        try:
            reps = DeepFace.represent(
                img_path=fpath,
                model_name=FACE_MODEL,
                detector_backend=FACE_DETECTOR,
                enforce_detection=False
            )
            if not reps:
                print(f"No face found in {fname}, skipping")
                continue

            # If facial_area present, crop then represent on crop
            facial_area = reps[0].get('facial_area') if isinstance(reps[0], dict) else None
            embedding = None
            if facial_area:
                try:
                    from PIL import Image
                    orig = Image.open(fpath).convert('RGB')
                    if isinstance(facial_area, (list, tuple)) and len(facial_area) == 4:
                        x, y, w, h = facial_area
                    elif isinstance(facial_area, dict) and {'x','y','w','h'}.issubset(facial_area.keys()):
                        x = facial_area['x']; y = facial_area['y']; w = facial_area['w']; h = facial_area['h']
                    else:
                        x = y = w = h = None

                    if x is not None:
                        left = int(max(0, x))
                        top = int(max(0, y))
                        right = int(min(orig.width, x + w))
                        bottom = int(min(orig.height, y + h))
                        pad_w = int((right - left) * 0.15)
                        pad_h = int((bottom - top) * 0.15)
                        left = max(0, left - pad_w)
                        top = max(0, top - pad_h)
                        right = min(orig.width, right + pad_w)
                        bottom = min(orig.height, bottom + pad_h)

                        crop = orig.crop((left, top, right, bottom))
                        import uuid
                        tmp_crop = os.path.join(os.path.dirname(fpath), f"tmp_rebuild_{uuid.uuid4().hex}.jpg")
                        crop.save(tmp_crop)
                        reps_crop = DeepFace.represent(
                            img_path=tmp_crop,
                            model_name=FACE_MODEL,
                            detector_backend=FACE_DETECTOR,
                            enforce_detection=False
                        )
                        if reps_crop and isinstance(reps_crop, list) and 'embedding' in reps_crop[0]:
                            embedding = np.array([reps_crop[0]['embedding']]).astype('float32')
                        try:
                            if os.path.exists(tmp_crop): os.remove(tmp_crop)
                        except Exception:
                            pass
                except Exception as e:
                    print(f"Failed to crop {fname}: {e}")

            if embedding is None:
                try:
                    embedding = np.array([reps[0]['embedding']]).astype('float32')
                except Exception:
                    print(f"No embedding for {fname}, skipping")
                    continue

            # Normalize
            try:
                e_norm = np.linalg.norm(embedding, axis=1, keepdims=True)
                e_norm[e_norm == 0] = 1.0
                embedding = embedding / e_norm
            except Exception:
                pass

            embeddings_list.append(embedding[0])
            labels_list.append(person_id)
            print(f"Added embedding from {fname} (person {person_id})")
        except Exception as e:
            print(f"❌ Error processing {fpath}: {e}")
            continue

    if not embeddings_list:
        print("No embeddings were produced from dataset")
        return 0

    # Convert to arrays
    all_embeddings = np.vstack(embeddings_list).astype('float32')
    labels_arr = np.array(labels_list, dtype=np.int64)

    # Collapse multiple embeddings per person into a single centroid to avoid
    # duplicate/identical vectors causing ambiguous matches. This also reduces
    # the index size and gives more stable per-person representatives.
    person_map = {}
    for emb, pid in zip(all_embeddings, labels_arr):
        if pid not in person_map:
            person_map[pid] = [emb]
        else:
            person_map[pid].append(emb)

    final_embeddings = []
    final_labels = []
    seen_keys = set()
    for pid, emb_list in person_map.items():
        try:
            centroid = np.mean(np.vstack(emb_list), axis=0)
        except Exception:
            centroid = emb_list[0]

        # Normalize centroid
        try:
            cnorm = np.linalg.norm(centroid)
            if cnorm == 0: cnorm = 1.0
            centroid = (centroid / cnorm).astype('float32')
        except Exception:
            centroid = centroid.astype('float32')

        # Create a stable key by rounding to 6 decimals to catch near-identical vectors
        key = tuple(np.round(centroid, 6).tolist())
        if key in seen_keys:
            print(f"Skipping duplicate centroid for person {pid}")
            continue
        seen_keys.add(key)
        final_embeddings.append(centroid)
        final_labels.append(pid)

    if not final_embeddings:
        print("No final embeddings after deduplication")
        return 0

    final_embeddings_arr = np.vstack(final_embeddings).astype('float32')
    final_labels_arr = np.array(final_labels, dtype=np.int64)

    # Build FAISS index
    dim = final_embeddings_arr.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(final_embeddings_arr)
    faiss.write_index(index, INDEX_PATH)
    np.save(LABELS_PATH, final_labels_arr)

    print(f"Rebuilt index with {len(final_labels_arr)} entries (collapsed from {len(labels_arr)})")
    return len(final_labels_arr)
