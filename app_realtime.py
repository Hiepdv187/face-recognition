from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import cv2
import numpy as np
from PIL import Image
import io
import base64
import json
from recognition import recognize_face
from embeddings import add_embedding, load_index
from config import SIM_THRESHOLD
from database import SessionLocal
from models import Person
import uuid
import warnings
warnings.filterwarnings("ignore", category=UserWarning)
import tensorflow as tf
tf.get_logger().setLevel("ERROR")
import sys

# On Windows consoles the default encoding may not support emoji/unicode used
# in some log prints. Reconfigure stdout/stderr to UTF-8 where possible and
# enable PYTHONUTF8 to reduce chance of UnicodeEncodeError crashing the app.
try:
    import os
    os.environ.setdefault('PYTHONUTF8', '1')
except Exception:
    pass

try:
    # Python 3.7+: reconfigure will set the encoding for stdout/stderr
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    # If reconfigure isn't available or fails, ignore and continue; prints
    # will be sanitized where necessary.
    pass

# Reduce TF logs and preload model to avoid per-request heavy initialization
try:
    import os
    os.environ.setdefault('TF_CPP_MIN_LOG_LEVEL', '2')
except Exception:
    pass

READY_MODEL = False
try:
    # Preload DeepFace model to warm TF and reduce per-request initialization cost
    from deepface import DeepFace
    from config import FACE_MODEL
    print('Loading face model:', FACE_MODEL)
    _ = DeepFace.build_model(FACE_MODEL)
    READY_MODEL = True
    print('Model preloaded')
except Exception as e:
    print('Model preload failed:', str(e))

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "dataset"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Store for real-time recognition results
recognition_cache = {}

@app.route('/')
def home():
    """Homepage với links đến các interfaces"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Face Recognition System</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; padding: 50px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #333; margin-bottom: 30px; }
            .links a { display: inline-block; margin: 10px; padding: 15px 30px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; }
            .links a:hover { background: #0056b3; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Face Recognition System</h1>
            <div class="links">
                <a href="/realtime">📹 Real-time Recognition</a>
                <a href="/smart-camera">🎥 Smart Camera (NEW)</a>
                <a href="/webcam">📹 Webcam Interface</a>
                <a href="/health">❤️ Health Check</a>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/realtime')
def realtime():
    """Real-time face recognition interface"""
    return send_from_directory('.', 'realtime_face_recognition.html')


@app.route('/dataset/<path:filename>')
def serve_dataset_file(filename):
    """Serve files from dataset folder (registered photos)."""
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/smart-camera')
def smart_camera():
    """Smart camera interface with overlay"""
    return send_from_directory('.', 'smart_camera.html')

@app.route('/webcam')
def webcam():
    """Simple webcam interface"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Webcam Face Recognition</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; text-align: center; }
            video, canvas { max-width: 500px; border: 2px solid #333; margin: 10px; }
            .result { font-size: 24px; font-weight: bold; margin: 20px; }
            button { padding: 10px 20px; margin: 10px; font-size: 16px; }
        </style>
    </head>
    <body>
        <h1>Webcam Face Recognition</h1>
        <video id="video" autoplay playsinline muted></video>
        <canvas id="canvas" style="display: none;"></canvas>
        <br>
        <button onclick="startRecognition()">Start Recognition</button>
        <button onclick="stopRecognition()">Stop Recognition</button>
        <br>
        <div id="result" style="color: #007bff;">Recognition: Stopped</div>
        <div id="status" style="margin-top: 20px; color: #666;"></div>

        <script>
            let video = document.getElementById('video');
            let canvas = document.getElementById('canvas');
            let ctx = canvas.getContext('2d');
            let stream = null;
            let recognitionInterval = null;

            async function startVideo() {
                try {
                    stream = await navigator.mediaDevices.getUserMedia({
                        video: { width: 640, height: 480 }
                    });
                    video.srcObject = stream;
                } catch (error) {
                    alert('Error accessing camera: ' + error.message);
                }
            }

            function startRecognition() {
                if (!stream) startVideo();

                recognitionInterval = setInterval(() => {
                    recognizeFrame();
                }, 2000);

                document.getElementById('result').textContent = 'Recognition: Active';
                document.getElementById('result').style.color = '#28a745';
                document.getElementById('status').textContent = 'Processing frames...';
            }

            function stopRecognition() {
                if (recognitionInterval) {
                    clearInterval(recognitionInterval);
                    recognitionInterval = null;
                }
                document.getElementById('result').textContent = 'Recognition: Stopped';
                document.getElementById('result').style.color = '#007bff';
                document.getElementById('status').textContent = '';
            }

            async function recognizeFrame() {
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
                ctx.drawImage(video, 0, 0);

                canvas.toBlob(async (blob) => {
                    const formData = new FormData();
                    formData.append('image', blob, 'frame.jpg');

                    try {
                        const response = await fetch('/api/face/recognize', {
                            method: 'POST',
                            body: formData
                        });
                        const result = await response.json();

                        const confidence = Math.round(result.distance * 100);
                        document.getElementById('result').textContent =
                            'Recognition: ' + (result.name || 'Unknown') + ' (' + confidence + '% confidence)';
                        document.getElementById('status').textContent =
                            result.name !== 'Unknown' ? 'Face recognized!' : 'No face recognized';

                    } catch (error) {
                        document.getElementById('result').textContent = 'Recognition: Error';
                        document.getElementById('result').style.color = '#dc3545';
                        document.getElementById('status').textContent = 'Connection error';
                    }
                });
            }

            startVideo();
        </script>
    </body>
    </html>
    '''

@app.route('/api/face/register', methods=['POST'])
def register_face():
    """Register face from uploaded image"""
    try:
        if 'image' not in request.files:
            return jsonify({"status": "error", "message": "No image provided"}), 400

        if 'name' not in request.form:
            return jsonify({"status": "error", "message": "No name provided"}), 400

        file = request.files['image']
        name = request.form['name']

        if file.filename == '':
            return jsonify({"status": "error", "message": "No image selected"}), 400

        # Read image bytes and convert
        img_bytes = file.read()
        try:
            img = Image.open(io.BytesIO(img_bytes)).convert('RGB')
        except Exception as e:
            import traceback
            print("❌ Failed to open uploaded image:", e)
            print(traceback.format_exc())
            return jsonify({"status": "error", "message": "Invalid image uploaded"}), 400

        session = SessionLocal()
        try:
            # Get or create person so we can name the file with person id
            person = session.query(Person).filter_by(name=name).first()
            if not person:
                person = Person(name=name)
                session.add(person)
                session.commit()
                session.refresh(person)

            # Save to file with person id prefix for easy lookup
            filename = f"{person.id}_{uuid.uuid4().hex}.jpg"
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            try:
                img.save(filepath)
            except Exception as e:
                import traceback
                print("❌ Failed to save uploaded image:", e)
                print(traceback.format_exc())
                return jsonify({"status": "error", "message": "Failed to save image"}), 500

            # Add embedding (may raise) and return meaningful errors
            try:
                success = add_embedding(filepath, person.id)
            except Exception as e:
                import traceback
                print(f"❌ Error adding embedding for person {person.id}: {e}")
                print(traceback.format_exc())
                return jsonify({"status": "error", "message": "Failed to add embedding"}), 500

            if success:
                # build absolute photo URL for convenience
                host = request.host_url.rstrip('/')
                photo_url = f"{host}/dataset/{filename}"
                return jsonify({
                    "status": "success",
                    "message": "Face registered successfully",
                    "person_id": person.id,
                    "name": person.name,
                    "photo": photo_url
                })
            else:
                return jsonify({"status": "error", "message": "Failed to add embedding"}), 500
        finally:
            try:
                session.close()
            except Exception:
                pass

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/face/recognize', methods=['POST'])
def recognize_face_api():
    """Recognize face from uploaded image"""
    try:
        print("🔍 Received recognition request")

        if 'image' not in request.files:
            print("❌ No image in request.files")
            return jsonify({"status": "error", "message": "No image provided"})

        file = request.files['image']

        if file.filename == '':
            print("❌ Empty filename")
            return jsonify({"status": "error", "message": "No image selected"})

        print(f"📁 Processing image: {file.filename}")

        # Read image
        img_bytes = file.read()
        print(f"📊 Image size: {len(img_bytes)} bytes")

        img = Image.open(io.BytesIO(img_bytes))

        # Save to temporary file
        filename = f"temp_{uuid.uuid4().hex}.jpg"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        img.save(filepath)
        print(f"💾 Saved to: {filepath}")

        # Recognize face: compute embedding and query index for top-1 match
        print("🤖 Starting face recognition...")
        try:
            from deepface import DeepFace
            reps = DeepFace.represent(img_path=filepath, model_name='ArcFace', detector_backend='mtcnn', enforce_detection=False)
        except Exception as e:
            print('Recognition deepface error:', e)
            try:
                os.remove(filepath)
            except Exception:
                pass
            return jsonify({'status': 'error', 'message': 'Failed to compute embedding'}), 500

        if not reps:
            try:
                os.remove(filepath)
            except Exception:
                pass
            return jsonify({'status': 'error', 'message': 'No face detected'}), 200

        # Try to crop for better embedding if facial_area provided
        embedding = None
        facial_area = reps[0].get('facial_area') if isinstance(reps[0], dict) else None
        if facial_area:
            try:
                from PIL import Image
                orig = Image.open(filepath).convert('RGB')
                if isinstance(facial_area, (list, tuple)) and len(facial_area) == 4:
                    x, y, w, h = facial_area
                elif isinstance(facial_area, dict) and {'x','y','w','h'}.issubset(facial_area.keys()):
                    x = facial_area['x']; y = facial_area['y']; w = facial_area['w']; h = facial_area['h']
                else:
                    x = y = w = h = None

                if x is not None:
                    left = int(max(0, x)); top = int(max(0, y))
                    right = int(min(orig.width, x + w)); bottom = int(min(orig.height, y + h))
                    pad_w = int((right - left) * 0.15); pad_h = int((bottom - top) * 0.15)
                    left = max(0, left - pad_w); top = max(0, top - pad_h)
                    right = min(orig.width, right + pad_w); bottom = min(orig.height, bottom + pad_h)
                    crop = orig.crop((left, top, right, bottom))
                    tmp_crop = os.path.join(UPLOAD_FOLDER, f"tmp_recog_crop_{uuid.uuid4().hex}.jpg")
                    crop.save(tmp_crop)
                    try:
                        reps_crop = DeepFace.represent(img_path=tmp_crop, model_name='ArcFace', detector_backend='mtcnn', enforce_detection=False)
                        if reps_crop and isinstance(reps_crop, list) and 'embedding' in reps_crop[0]:
                            embedding = np.array(reps_crop[0]['embedding'], dtype='float32')
                    finally:
                        try: os.remove(tmp_crop)
                        except: pass
            except Exception:
                embedding = None

        if embedding is None:
            try:
                embedding = np.array(reps[0]['embedding'], dtype='float32')
            except Exception:
                try:
                    os.remove(filepath)
                except Exception:
                    pass
                return jsonify({'status': 'error', 'message': 'Failed to extract embedding'}), 500

        # Normalize
        try:
            qnorm = np.linalg.norm(embedding)
            if qnorm == 0: qnorm = 1.0
            qvec = (embedding / qnorm).astype('float32')
        except Exception:
            qvec = embedding.astype('float32')

        # Query FAISS
        index, labels = load_index()
        if index is None or labels is None:
            try:
                os.remove(filepath)
            except Exception:
                pass
            return jsonify({'status': 'error', 'message': 'Index or labels missing'}), 500

        D, I = index.search(np.array([qvec]), 1)
        best_idx = int(I[0][0])
        raw_dist = float(D[0][0])

        # Try to reconstruct vector for accurate L2 and cosine
        vec = None
        try:
            vec = np.zeros((index.d,), dtype='float32')
            index.reconstruct(best_idx, vec)
        except Exception:
            vec = None

        l2 = raw_dist if vec is None else float(np.linalg.norm(qvec - vec))
        cosine = None
        if vec is not None:
            try:
                cosine = float(np.dot(qvec, vec) / (np.linalg.norm(qvec) * (np.linalg.norm(vec) or 1.0)))
            except Exception:
                cosine = None

        person_id = int(labels[best_idx]) if labels is not None and len(labels) > best_idx else None
        name = None
        photo = None
        try:
            session = SessionLocal()
            p = session.query(Person).filter_by(id=person_id).first()
            if p:
                name = p.name
                # find photo
                for fname in os.listdir(UPLOAD_FOLDER):
                    if fname.startswith(f"{person_id}_"):
                        host = request.host_url.rstrip('/')
                        photo = f"{host}/dataset/{fname}"
                        break
            session.close()
        except Exception:
            name = None

        # Clean up temp file
        try:
            os.remove(filepath)
        except:
            pass

        # Build confidence from cosine if available, else from l2
        if cosine is not None:
            # map [-1,1] -> [0,1]
            confidence = max(0.0, min(1.0, (cosine + 1.0) / 2.0))
        else:
            confidence = 1.0 / (1.0 + max(0.0, l2 or 1e9))

        # Apply similarity threshold for recognition decision
        if confidence < SIM_THRESHOLD:
            person_id = None
            name = 'Unknown'

        return jsonify({
            'status': 'success',
            'person_id': person_id,
            'name': name or 'Unknown',
            'l2': l2,
            'cosine': cosine,
            'distance': l2,
            'confidence': confidence,
            'photo': photo
        })

    except Exception as e:
        print(f"❌ Recognition error: {str(e)}")
        import traceback
        print("📋 Traceback:", traceback.format_exc())
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/face/persons', methods=['GET'])
def get_persons():
    """Get all registered persons"""
    try:
        session = SessionLocal()
        persons = session.query(Person).all()

        result = []
        for person in persons:
            # try to find an image file with prefix {person.id}_ in dataset
            photo_url = None
            try:
                for fname in os.listdir(UPLOAD_FOLDER):
                    if fname.startswith(f"{person.id}_"):
                        # make absolute URL
                        host = request.host_url.rstrip('/')
                        photo_url = f"{host}/dataset/{fname}"
                        break
            except Exception:
                photo_url = None

            result.append({
                "id": person.id,
                "name": person.name,
                "photo": photo_url
            })

        session.close()
        return jsonify({"status": "success", "persons": result})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/face/debug')
def debug_status():
    """Debug endpoint to check system status"""
    try:
        # Check FAISS index
        index_exists = os.path.exists(os.path.join("embeddings", "face_index.faiss"))
        labels_exists = os.path.exists(os.path.join("embeddings", "labels.npy"))

        # Check database
        session = SessionLocal()
        persons = session.query(Person).all()
        session.close()

        # Check dataset
        dataset_files = os.listdir(UPLOAD_FOLDER) if os.path.exists(UPLOAD_FOLDER) else []

        return jsonify({
            "status": "debug",
            "faiss_index": "exists" if index_exists else "missing",
            "labels": "exists" if labels_exists else "missing",
            "registered_persons": len(persons),
            "dataset_files": len(dataset_files),
            "persons": [{"id": p.id, "name": p.name} for p in persons],
            "recent_dataset": dataset_files[-5:] if dataset_files else []
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        })


@app.route('/api/face/rebuild', methods=['POST'])
def rebuild_index():
    """Trigger a rebuild of the FAISS index from dataset files."""
    try:
        from embeddings import rebuild_index_from_dataset
        count = rebuild_index_from_dataset(UPLOAD_FOLDER)
        return jsonify({"status": "success", "message": "Rebuilt index", "entries": count})
    except Exception as e:
        import traceback
        print("❌ Rebuild error:", traceback.format_exc())
        return jsonify({"status": "error", "message": str(e)})


@app.route('/api/face/compare', methods=['POST'])
def compare_face():
    """Return embedding and top-K matches (label, L2, cosine) for debugging/tuning."""
    try:
        if 'image' not in request.files:
            return jsonify({'status': 'error', 'message': 'No image provided'}), 400

        file = request.files['image']
        if file.filename == '':
            return jsonify({'status': 'error', 'message': 'Empty filename'}), 400

        # Save temp
        img_bytes = file.read()
        from PIL import Image
        import os, uuid
        tmp_path = os.path.join(UPLOAD_FOLDER, f"tmp_compare_{uuid.uuid4().hex}.jpg")
        try:
            img = Image.open(io.BytesIO(img_bytes)).convert('RGB')
            img.save(tmp_path)
        except Exception as e:
            return jsonify({'status': 'error', 'message': 'Invalid image'}), 400

        # Compute embedding similarly to registration/recognition
        try:
            from deepface import DeepFace
            reps = DeepFace.represent(img_path=tmp_path, model_name='ArcFace', detector_backend='mtcnn', enforce_detection=False)
        except Exception as e:
            os.remove(tmp_path)
            return jsonify({'status': 'error', 'message': f'DeepFace error: {str(e)}'}), 500

        if not reps:
            os.remove(tmp_path)
            return jsonify({'status': 'error', 'message': 'No face detected'}), 200

        # Try to use facial_area to crop and recompute embedding for accuracy
        embedding = None
        facial_area = reps[0].get('facial_area') if isinstance(reps[0], dict) else None
        if facial_area:
            try:
                orig = Image.open(tmp_path).convert('RGB')
                if isinstance(facial_area, (list, tuple)) and len(facial_area) == 4:
                    x, y, w, h = facial_area
                elif isinstance(facial_area, dict) and {'x','y','w','h'}.issubset(facial_area.keys()):
                    x = facial_area['x']; y = facial_area['y']; w = facial_area['w']; h = facial_area['h']
                else:
                    x = y = w = h = None

                if x is not None:
                    left = int(max(0, x)); top = int(max(0, y))
                    right = int(min(orig.width, x + w)); bottom = int(min(orig.height, y + h))
                    pad_w = int((right - left) * 0.15); pad_h = int((bottom - top) * 0.15)
                    left = max(0, left - pad_w); top = max(0, top - pad_h)
                    right = min(orig.width, right + pad_w); bottom = min(orig.height, bottom + pad_h)
                    crop = orig.crop((left, top, right, bottom))
                    tmp_crop = os.path.join(UPLOAD_FOLDER, f"tmp_compare_crop_{uuid.uuid4().hex}.jpg")
                    crop.save(tmp_crop)
                    try:
                        reps_crop = DeepFace.represent(img_path=tmp_crop, model_name='ArcFace', detector_backend='mtcnn', enforce_detection=False)
                        if reps_crop and isinstance(reps_crop, list) and 'embedding' in reps_crop[0]:
                            embedding = np.array(reps_crop[0]['embedding'], dtype='float32')
                    finally:
                        try: os.remove(tmp_crop)
                        except: pass
            except Exception:
                embedding = None

        if embedding is None:
            try:
                embedding = np.array(reps[0]['embedding'], dtype='float32')
            except Exception:
                os.remove(tmp_path)
                return jsonify({'status': 'error', 'message': 'Failed to extract embedding'}), 500

        # Normalize query
        try:
            qnorm = np.linalg.norm(embedding)
            if qnorm == 0: qnorm = 1.0
            qvec = (embedding / qnorm).astype('float32')
        except Exception:
            qvec = embedding.astype('float32')

        # Load index
        index, labels = load_index()
        if index is None or labels is None:
            os.remove(tmp_path)
            return jsonify({'status': 'error', 'message': 'Index or labels missing'}), 500

        k = int(request.args.get('k', 5))
        # Cap k to the number of entries in the index to avoid -1/NaN results
        k = max(1, min(k, int(index.ntotal)))
        D, I = index.search(np.array([qvec]), k)

        results = []
        for dist_list, idx_list in zip(D, I):
            for dist, idx in zip(dist_list, idx_list):
                if int(idx) < 0:
                    # invalid index returned by FAISS when k > ntotal
                    continue

                try:
                    vec = np.zeros((index.d, ), dtype='float32')
                    index.reconstruct(int(idx), vec)
                except Exception:
                    # if reconstruct not supported, treat vec as None
                    vec = None

                # compute l2 and cosine safely
                try:
                    l2 = float(dist) if vec is None else float(np.linalg.norm(qvec - vec))
                except Exception:
                    l2 = None

                cos = None
                if vec is not None:
                    try:
                        cos = float(np.dot(qvec, vec) / (np.linalg.norm(qvec) * (np.linalg.norm(vec) or 1.0)))
                    except Exception:
                        cos = None

                person_id = int(labels[int(idx)]) if labels is not None and len(labels) > int(idx) else None
                # lookup name
                name = None
                try:
                    session = SessionLocal()
                    p = session.query(Person).filter_by(id=person_id).first()
                    if p:
                        name = p.name
                    session.close()
                except Exception:
                    name = None

                results.append({
                    'label_index': int(idx),
                    'person_id': person_id,
                    'name': name,
                    'l2': l2,
                    'cosine': cos
                })

        os.remove(tmp_path)
        return jsonify({'status': 'success', 'results': results, 'query_norm': float(np.linalg.norm(qvec))})

    except Exception as e:
        import traceback
        print('Compare error:', traceback.format_exc())
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "face-recognition",
        "message": "Face recognition service is running"
    })

if __name__ == '__main__':
    print("🚀 Starting Face Recognition Flask Server...")
    print("📡 Available endpoints:")
    print("   GET  /                    - Homepage")
    print("   GET  /realtime           - Real-time recognition page")
    print("   GET  /smart-camera       - Smart camera with overlay (NEW)")
    print("   GET  /webcam             - Webcam interface")
    print("   GET  /health             - Health check")
    print("   POST /api/face/register  - Register face")
    print("   POST /api/face/recognize - Recognize face")
    print("   GET  /api/face/persons   - Get all persons")
    print("   GET  /api/face/debug     - Debug system status")
    print("   GET  /api/face/realtime/status - Real-time status")
    print("")
    print("🌐 Server running on http://localhost:5000")
    print("🎥 Open http://localhost:5000/smart-camera for smart camera interface")
    print("📹 Open http://localhost:5000/realtime for real-time recognition")

    # Run without the auto-reloader to avoid double initialization which can
    # trigger background flushes (e.g. lz4 frame flush on process exit) and
    # cause "I/O operation on closed file" warnings. When debugging, you can
    # still set debug=True but keep use_reloader=False.
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
