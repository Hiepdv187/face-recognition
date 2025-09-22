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
from embeddings import add_embedding
from database import SessionLocal
from models import Person
import uuid
import warnings
warnings.filterwarnings("ignore", category=UserWarning)
import tensorflow as tf
tf.get_logger().setLevel("ERROR")

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
            return jsonify({"status": "error", "message": "No image provided"})

        if 'name' not in request.form:
            return jsonify({"status": "error", "message": "No name provided"})

        file = request.files['image']
        name = request.form['name']

        if file.filename == '':
            return jsonify({"status": "error", "message": "No image selected"})

        # Read image
        img_bytes = file.read()
        img = Image.open(io.BytesIO(img_bytes))

        # Save to file
        filename = f"register_{uuid.uuid4().hex}.jpg"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        img.save(filepath)

        # Get or create person
        session = SessionLocal()
        person = session.query(Person).filter_by(name=name).first()
        if not person:
            person = Person(name=name)
            session.add(person)
            session.commit()

        # Add embedding
        if add_embedding(filepath, person.id):
            session.close()
            return jsonify({
                "status": "success",
                "message": "Face registered successfully",
                "person_id": person.id,
                "name": person.name
            })
        else:
            session.close()
            return jsonify({"status": "error", "message": "Failed to add embedding"})

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

        # Recognize face
        print("🤖 Starting face recognition...")
        name, distance = recognize_face(filepath)
        print(f"✅ Recognition result: name={name}, distance={distance}")

        # Clean up temp file
        try:
            os.remove(filepath)
            print(f"🗑️ Cleaned up: {filepath}")
        except:
            print(f"⚠️ Failed to clean up: {filepath}")
            pass

        return jsonify({
            "status": "success",
            "name": name,
            "distance": distance
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
            result.append({
                "id": person.id,
                "name": person.name
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

    app.run(host='0.0.0.0', port=5000, debug=True)
