import cv2
from ultralytics import YOLO
from flask import Flask, render_template_string, Response

app = Flask(__name__)
model = YOLO('yolov8n.pt')

COLORS = [
    (255, 99, 71), (50, 205, 50), (30, 144, 255), (255, 215, 0),
    (255, 0, 255), (0, 255, 255), (255, 165, 0), (138, 43, 226)
]

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Object Detection</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            min-height: 100vh;
            font-family: Arial, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 30px 20px;
        }
        h1 {
            color: #fff;
            font-size: 2rem;
            margin-bottom: 8px;
            text-shadow: 0 0 20px #a78bfa;
        }
        .subtitle {
            color: #a78bfa;
            margin-bottom: 30px;
            font-size: 1rem;
            letter-spacing: 2px;
            text-transform: uppercase;
        }
        .video-container {
            border: 3px solid #a78bfa;
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 0 40px rgba(167, 139, 250, 0.4);
            margin-bottom: 30px;
        }
        img {
            display: block;
            width: 700px;
            max-width: 100%;
        }
        .badges {
            display: flex;
            gap: 16px;
            flex-wrap: wrap;
            justify-content: center;
        }
        .badge {
            background: rgba(255,255,255,0.08);
            border: 1px solid rgba(167,139,250,0.4);
            color: #fff;
            padding: 10px 22px;
            border-radius: 50px;
            font-size: 0.9rem;
            backdrop-filter: blur(10px);
        }
        .badge span { color: #a78bfa; font-weight: bold; }
        .dot {
            display: inline-block;
            width: 10px; height: 10px;
            background: #50cd50;
            border-radius: 50%;
            margin-right: 6px;
            animation: pulse 1.5s infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.3; }
        }
    </style>
</head>
<body>
    <h1>🎯 Object Detection</h1>
    <p class="subtitle">Powered by YOLOv8 · Real Time AI</p>
    <div class="video-container">
        <img src="/video_feed" />
    </div>
    <div class="badges">
        <div class="badge"><span class="dot"></span>Live Feed Active</div>
        <div class="badge">Model: <span>YOLOv8n</span></div>
        <div class="badge">Confidence: <span>&gt; 50%</span></div>
        <div class="badge">Press <span>Q</span> in terminal to quit</div>
    </div>
</body>
</html>
'''

def generate_frames():
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        results = model(frame, verbose=False)

        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                confidence = float(box.conf[0])
                class_id = int(box.cls[0])
                label = model.names[class_id]
                color = COLORS[class_id % len(COLORS)]

                if confidence > 0.5:
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                    cv2.rectangle(frame, (x1, y1 - 30), (x2, y1), color, -1)
                    text = f"{label} {confidence:.0%}"
                    cv2.putText(frame, text, (x1 + 5, y1 - 8),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        ret2, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    print("Open your browser at http://127.0.0.1:5002")
    app.run(debug=False, port=5002, host='0.0.0.0')