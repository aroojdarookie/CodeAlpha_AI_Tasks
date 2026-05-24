from flask import Flask, render_template_string, send_file, request
import numpy as np
from midiutil import MIDIFile
import io
import random

app = Flask(__name__)

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>AI Music Generator</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            background: #050510;
            min-height: 100vh;
            font-family: 'Arial', sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 40px 20px;
            overflow-x: hidden;
        }

        .stars {
            position: fixed;
            top: 0; left: 0;
            width: 100%; height: 100%;
            pointer-events: none;
            z-index: 0;
        }

        .star {
            position: absolute;
            background: white;
            border-radius: 50%;
            animation: twinkle 3s infinite;
        }

        @keyframes twinkle {
            0%, 100% { opacity: 0.2; }
            50% { opacity: 1; }
        }

        .content {
            position: relative;
            z-index: 1;
            width: 100%;
            max-width: 650px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        .logo {
            font-size: 4rem;
            margin-bottom: 10px;
            animation: float 3s ease-in-out infinite;
        }

        @keyframes float {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
        }

        h1 {
            font-size: 2.8rem;
            font-weight: 900;
            background: linear-gradient(90deg, #ff6eb4, #a78bfa, #60a5fa, #34d399);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-size: 300% 300%;
            animation: gradientShift 4s ease infinite;
            text-align: center;
            margin-bottom: 8px;
        }

        @keyframes gradientShift {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        .subtitle {
            color: #6b7280;
            letter-spacing: 3px;
            text-transform: uppercase;
            font-size: 0.75rem;
            margin-bottom: 50px;
        }

        .card {
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(167,139,250,0.2);
            border-radius: 24px;
            padding: 40px;
            width: 100%;
            backdrop-filter: blur(20px);
            box-shadow: 0 0 60px rgba(167,139,250,0.1), inset 0 1px 0 rgba(255,255,255,0.05);
        }

        .genre-grid {
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 10px;
            margin-bottom: 32px;
        }

        .genre-btn {
            background: rgba(255,255,255,0.04);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 12px;
            padding: 14px 6px;
            color: #9ca3af;
            cursor: pointer;
            text-align: center;
            transition: all 0.2s;
            font-size: 0.8rem;
        }

        .genre-btn:hover {
            border-color: #a78bfa;
            color: #a78bfa;
            background: rgba(167,139,250,0.1);
        }

        .genre-btn.active {
            border-color: #a78bfa;
            background: rgba(167,139,250,0.15);
            color: #a78bfa;
            box-shadow: 0 0 20px rgba(167,139,250,0.2);
        }

        .genre-icon { font-size: 1.5rem; display: block; margin-bottom: 6px; }

        .hidden-select { display: none; }

        .slider-group {
            margin-bottom: 28px;
        }

        .slider-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }

        .slider-label {
            color: #9ca3af;
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .slider-value {
            color: #f472b6;
            font-weight: bold;
            font-size: 0.95rem;
            background: rgba(244,114,182,0.1);
            padding: 4px 12px;
            border-radius: 20px;
            border: 1px solid rgba(244,114,182,0.3);
        }

        input[type=range] {
            width: 100%;
            height: 6px;
            -webkit-appearance: none;
            background: rgba(255,255,255,0.08);
            border-radius: 3px;
            outline: none;
        }

        input[type=range]::-webkit-slider-thumb {
            -webkit-appearance: none;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background: linear-gradient(135deg, #f472b6, #a78bfa);
            cursor: pointer;
            box-shadow: 0 0 10px rgba(244,114,182,0.5);
        }

        .generate-btn {
            width: 100%;
            padding: 18px;
            background: linear-gradient(135deg, #7c3aed, #db2777, #2563eb);
            background-size: 200% 200%;
            animation: gradientShift 3s ease infinite;
            border: none;
            border-radius: 14px;
            color: white;
            font-size: 1.1rem;
            font-weight: bold;
            cursor: pointer;
            letter-spacing: 1px;
            box-shadow: 0 4px 30px rgba(124,58,237,0.4);
            transition: transform 0.1s;
        }

        .generate-btn:hover { transform: scale(1.02); }
        .generate-btn:active { transform: scale(0.98); }

        .result-card {
            margin-top: 24px;
            background: rgba(50,205,50,0.05);
            border: 1px solid rgba(50,205,50,0.2);
            border-radius: 16px;
            padding: 24px;
            text-align: center;
        }

        .result-title {
            color: #34d399;
            font-size: 1rem;
            margin-bottom: 20px;
            letter-spacing: 1px;
        }

        .visualizer {
            display: flex;
            align-items: flex-end;
            justify-content: center;
            gap: 3px;
            height: 70px;
            margin-bottom: 24px;
        }

        .bar {
            width: 6px;
            border-radius: 3px;
            animation: dance 0.8s ease-in-out infinite alternate;
        }

        @keyframes dance {
            from { transform: scaleY(0.2); }
            to { transform: scaleY(1); }
        }

        .download-btn {
            display: inline-flex;
            align-items: center;
            gap: 10px;
            padding: 14px 32px;
            background: rgba(96,165,250,0.1);
            border: 1px solid rgba(96,165,250,0.4);
            border-radius: 12px;
            color: #60a5fa;
            text-decoration: none;
            font-size: 1rem;
            transition: all 0.2s;
        }

        .download-btn:hover {
            background: rgba(96,165,250,0.2);
            box-shadow: 0 0 20px rgba(96,165,250,0.3);
        }

        .info-row {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-top: 16px;
            flex-wrap: wrap;
        }

        .info-badge {
            background: rgba(255,255,255,0.04);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 20px;
            padding: 6px 16px;
            font-size: 0.8rem;
            color: #6b7280;
        }

        .info-badge span { color: #a78bfa; }
    </style>
</head>
<body>
    <div class="stars" id="stars"></div>

    <div class="content">
        <div class="logo">🎵</div>
        <h1>AI Music Generator</h1>
        <p class="subtitle">Neural Pattern · MIDI Synthesis · Real Time</p>

        <div class="card">
            <form method="POST" id="musicForm">

                <div style="margin-bottom: 12px;">
                    <div class="slider-label" style="margin-bottom: 14px;">Select Genre</div>
                    <div class="genre-grid">
                        <div class="genre-btn active" onclick="selectGenre('classical', this)">
                            <span class="genre-icon">🎼</span>Classical
                        </div>
                        <div class="genre-btn" onclick="selectGenre('jazz', this)">
                            <span class="genre-icon">🎷</span>Jazz
                        </div>
                        <div class="genre-btn" onclick="selectGenre('happy', this)">
                            <span class="genre-icon">😊</span>Happy
                        </div>
                        <div class="genre-btn" onclick="selectGenre('sad', this)">
                            <span class="genre-icon">🌧️</span>Sad
                        </div>
                        <div class="genre-btn" onclick="selectGenre('random', this)">
                            <span class="genre-icon">🎲</span>Random
                        </div>
                    </div>
                    <input type="hidden" name="genre" id="genreInput" value="classical">
                </div>

                <div class="slider-group">
                    <div class="slider-header">
                        <span class="slider-label">Tempo</span>
                        <span class="slider-value" id="tempoVal">120 BPM</span>
                    </div>
                    <input type="range" name="tempo" min="60" max="180" value="120"
                           oninput="document.getElementById('tempoVal').textContent=this.value+' BPM'">
                </div>

                <div class="slider-group">
                    <div class="slider-header">
                        <span class="slider-label">Number of Notes</span>
                        <span class="slider-value" id="notesVal">32 Notes</span>
                    </div>
                    <input type="range" name="notes" min="16" max="64" value="32"
                           oninput="document.getElementById('notesVal').textContent=this.value+' Notes'">
                </div>

                <button type="submit" class="generate-btn">✨ Generate Music with AI</button>
            </form>

            {% if generated %}
            <div class="result-card">
                <p class="result-title">✅ YOUR MUSIC IS READY</p>
                <div class="visualizer" id="viz"></div>
                <a href="/download" class="download-btn">⬇️ Download MIDI File</a>
                <div class="info-row">
                    <div class="info-badge">Genre: <span>{{ genre }}</span></div>
                    <div class="info-badge">Tempo: <span>{{ tempo }} BPM</span></div>
                    <div class="info-badge">Notes: <span>{{ notes }}</span></div>
                </div>
            </div>
            {% endif %}
        </div>
    </div>

    <script>
        // Stars background
        const starsEl = document.getElementById('stars');
        for (let i = 0; i < 80; i++) {
            const star = document.createElement('div');
            star.className = 'star';
            const size = Math.random() * 2 + 1;
            star.style.cssText = `width:${size}px;height:${size}px;top:${Math.random()*100}%;left:${Math.random()*100}%;animation-delay:${Math.random()*3}s;animation-duration:${2+Math.random()*3}s`;
            starsEl.appendChild(star);
        }

        // Genre selector
        function selectGenre(genre, el) {
            document.querySelectorAll('.genre-btn').forEach(b => b.classList.remove('active'));
            el.classList.add('active');
            document.getElementById('genreInput').value = genre;
        }

        // Visualizer bars
        const viz = document.getElementById('viz');
        if (viz) {
            const colors = ['#f472b6','#a78bfa','#60a5fa','#34d399','#fbbf24'];
            for (let i = 0; i < 30; i++) {
                const bar = document.createElement('div');
                bar.className = 'bar';
                const h = Math.random() * 50 + 20;
                bar.style.cssText = `height:${h}px;background:${colors[i%colors.length]};animation-delay:${Math.random()*0.8}s;animation-duration:${0.4+Math.random()*0.6}s`;
                viz.appendChild(bar);
            }
        }
    </script>
</body>
</html>
'''

SCALES = {
    'classical': [60, 62, 64, 65, 67, 69, 71, 72],
    'jazz':      [60, 62, 63, 65, 67, 68, 70, 72],
    'happy':     [60, 62, 64, 67, 69, 72, 74, 76],
    'sad':       [60, 62, 63, 65, 67, 68, 70, 72],
    'random':    [60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72]
}

last_midi = None
last_genre = 'classical'
last_tempo = 120
last_notes = 32

def generate_midi(genre, tempo, num_notes):
    scale = SCALES.get(genre, SCALES['classical'])
    midi = MIDIFile(1)
    midi.addTempo(0, 0, tempo)
    prev_note = random.choice(scale)
    for i in range(num_notes):
        neighbors = [n for n in scale if abs(n - prev_note) <= 4]
        note = random.choice(neighbors if neighbors else scale)
        duration = random.choice([0.5, 1, 1.5, 2])
        velocity = random.randint(70, 110)
        midi.addNote(0, 0, note, i * 0.5, duration, velocity)
        prev_note = note
    buf = io.BytesIO()
    midi.writeFile(buf)
    buf.seek(0)
    return buf

@app.route('/', methods=['GET', 'POST'])
def index():
    global last_midi, last_genre, last_tempo, last_notes
    generated = False
    if request.method == 'POST':
        last_genre = request.form.get('genre', 'classical')
        last_tempo = int(request.form.get('tempo', 120))
        last_notes = int(request.form.get('notes', 32))
        last_midi = generate_midi(last_genre, last_tempo, last_notes)
        generated = True
    return render_template_string(HTML, generated=generated,
                                  genre=last_genre, tempo=last_tempo, notes=last_notes)

@app.route('/download')
def download():
    global last_midi
    if last_midi is None:
        return "No music generated yet!", 400
    last_midi.seek(0)
    return send_file(last_midi, mimetype='audio/midi',
                    as_attachment=True, download_name='ai_music.mid')

if __name__ == '__main__':
    print("Open your browser at http://127.0.0.1:5003")
    app.run(debug=False, port=5003)