from flask import Flask, render_template_string, request
from deep_translator import GoogleTranslator

app = Flask(__name__)

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>AI Translator</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            min-height: 100vh;
            background: #020008;
            font-family: 'Arial', sans-serif;
            overflow-x: hidden;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 40px 20px;
        }

        /* Animated background orbs */
        .orb {
            position: fixed;
            border-radius: 50%;
            filter: blur(80px);
            opacity: 0.15;
            pointer-events: none;
            animation: orbFloat 8s ease-in-out infinite;
        }
        .orb1 { width: 500px; height: 500px; background: #7c3aed; top: -100px; left: -100px; animation-delay: 0s; }
        .orb2 { width: 400px; height: 400px; background: #db2777; top: 50%; right: -100px; animation-delay: 2s; }
        .orb3 { width: 350px; height: 350px; background: #2563eb; bottom: -100px; left: 30%; animation-delay: 4s; }

        @keyframes orbFloat {
            0%, 100% { transform: translateY(0) scale(1); }
            50% { transform: translateY(-30px) scale(1.05); }
        }

        /* Grid lines background */
        .grid-bg {
            position: fixed;
            top: 0; left: 0;
            width: 100%; height: 100%;
            background-image:
                linear-gradient(rgba(167,139,250,0.03) 1px, transparent 1px),
                linear-gradient(90deg, rgba(167,139,250,0.03) 1px, transparent 1px);
            background-size: 50px 50px;
            pointer-events: none;
        }

        .content {
            position: relative;
            z-index: 1;
            width: 100%;
            max-width: 900px;
        }

        /* Header */
        .header {
            text-align: center;
            margin-bottom: 50px;
        }

        .badge {
            display: inline-block;
            background: rgba(124,58,237,0.2);
            border: 1px solid rgba(124,58,237,0.4);
            color: #a78bfa;
            padding: 6px 20px;
            border-radius: 20px;
            font-size: 0.75rem;
            letter-spacing: 3px;
            text-transform: uppercase;
            margin-bottom: 20px;
        }

        h1 {
            font-size: 3.5rem;
            font-weight: 900;
            line-height: 1.1;
            margin-bottom: 16px;
        }

        .gradient-text {
            background: linear-gradient(135deg, #ffffff 0%, #a78bfa 50%, #f472b6 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .header p {
            color: #4b5563;
            font-size: 1rem;
            letter-spacing: 2px;
            text-transform: uppercase;
        }

        /* 3D Card */
        .translator-card {
            background: rgba(255,255,255,0.02);
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 28px;
            padding: 40px;
            backdrop-filter: blur(40px);
            box-shadow:
                0 0 0 1px rgba(255,255,255,0.04),
                0 20px 60px rgba(0,0,0,0.5),
                0 0 100px rgba(124,58,237,0.08),
                inset 0 1px 0 rgba(255,255,255,0.06);
            transform: perspective(1000px) rotateX(1deg);
            transition: transform 0.3s ease;
        }

        .translator-card:hover {
            transform: perspective(1000px) rotateX(0deg) translateY(-4px);
        }

        /* Language selectors row */
        .lang-row {
            display: grid;
            grid-template-columns: 1fr auto 1fr;
            gap: 16px;
            align-items: center;
            margin-bottom: 24px;
        }

        .lang-select-wrap {
            position: relative;
        }

        .lang-label {
            font-size: 0.7rem;
            color: #6b7280;
            text-transform: uppercase;
            letter-spacing: 2px;
            margin-bottom: 8px;
        }

        select {
            width: 100%;
            padding: 14px 18px;
            background: rgba(255,255,255,0.04);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 14px;
            color: white;
            font-size: 0.95rem;
            outline: none;
            cursor: pointer;
            transition: all 0.2s;
            appearance: none;
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%236b7280' d='M6 8L1 3h10z'/%3E%3C/svg%3E");
            background-repeat: no-repeat;
            background-position: right 16px center;
        }

        select:focus {
            border-color: rgba(167,139,250,0.5);
            background-color: rgba(167,139,250,0.05);
            box-shadow: 0 0 0 3px rgba(167,139,250,0.1);
        }

        select option { background: #0d0d1a; }

        .swap-btn {
            width: 44px;
            height: 44px;
            background: rgba(167,139,250,0.1);
            border: 1px solid rgba(167,139,250,0.3);
            border-radius: 12px;
            color: #a78bfa;
            font-size: 1.1rem;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-top: 22px;
            transition: all 0.2s;
        }

        .swap-btn:hover {
            background: rgba(167,139,250,0.2);
            transform: rotate(180deg);
        }

        /* Text areas */
        .areas-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 16px;
            margin-bottom: 24px;
        }

        .area-wrap {
            position: relative;
        }

        .area-label {
            font-size: 0.7rem;
            color: #6b7280;
            text-transform: uppercase;
            letter-spacing: 2px;
            margin-bottom: 8px;
        }

        textarea {
            width: 100%;
            height: 180px;
            padding: 18px;
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.07);
            border-radius: 16px;
            color: white;
            font-size: 1rem;
            resize: none;
            outline: none;
            line-height: 1.6;
            transition: all 0.2s;
        }

        textarea:focus {
            border-color: rgba(167,139,250,0.4);
            background: rgba(167,139,250,0.04);
            box-shadow: 0 0 0 3px rgba(167,139,250,0.08);
        }

        textarea::placeholder { color: #374151; }

        .result-area {
            background: rgba(167,139,250,0.04);
            border-color: rgba(167,139,250,0.15);
            color: #e5e7eb;
        }

        /* Translate button */
        .btn-wrap { text-align: center; }

        .translate-btn {
            position: relative;
            padding: 16px 60px;
            background: linear-gradient(135deg, #7c3aed, #db2777);
            border: none;
            border-radius: 14px;
            color: white;
            font-size: 1rem;
            font-weight: bold;
            letter-spacing: 2px;
            text-transform: uppercase;
            cursor: pointer;
            overflow: hidden;
            transition: all 0.3s;
            box-shadow: 0 4px 30px rgba(124,58,237,0.4), 0 0 0 1px rgba(255,255,255,0.05);
        }

        .translate-btn::before {
            content: '';
            position: absolute;
            top: 0; left: -100%;
            width: 100%; height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
            transition: left 0.5s;
        }

        .translate-btn:hover::before { left: 100%; }

        .translate-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 40px rgba(124,58,237,0.6), 0 0 0 1px rgba(255,255,255,0.1);
        }

        .translate-btn:active { transform: translateY(0); }

        /* Stats row */
        .stats-row {
            display: flex;
            justify-content: center;
            gap: 30px;
            margin-top: 40px;
        }

        .stat {
            text-align: center;
        }

        .stat-num {
            font-size: 1.8rem;
            font-weight: 900;
            background: linear-gradient(135deg, #a78bfa, #f472b6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .stat-label {
            font-size: 0.7rem;
            color: #4b5563;
            text-transform: uppercase;
            letter-spacing: 2px;
            margin-top: 4px;
        }

        .divider {
            width: 1px;
            height: 40px;
            background: rgba(255,255,255,0.06);
            align-self: center;
        }

        /* Copy button */
        .copy-btn {
            position: absolute;
            top: 36px;
            right: 12px;
            background: rgba(255,255,255,0.06);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 8px;
            color: #6b7280;
            padding: 6px 10px;
            font-size: 0.75rem;
            cursor: pointer;
            transition: all 0.2s;
        }

        .copy-btn:hover {
            background: rgba(167,139,250,0.1);
            color: #a78bfa;
            border-color: rgba(167,139,250,0.3);
        }

        /* Floating particles */
        .particle {
            position: fixed;
            border-radius: 50%;
            pointer-events: none;
            animation: particleFloat linear infinite;
            opacity: 0;
        }

        @keyframes particleFloat {
            0% { transform: translateY(100vh) rotate(0deg); opacity: 0; }
            10% { opacity: 0.6; }
            90% { opacity: 0.6; }
            100% { transform: translateY(-100px) rotate(720deg); opacity: 0; }
        }
    </style>
</head>
<body>
    <div class="orb orb1"></div>
    <div class="orb orb2"></div>
    <div class="orb orb3"></div>
    <div class="grid-bg"></div>

    <div class="content">
        <div class="header">
            <div class="badge">⚡ Powered by Google AI</div>
            <h1><span class="gradient-text">Language Translation</span></h1>
            <p>Break every language barrier · Instantly</p>
        </div>

        <div class="translator-card">
            <form method="POST">
                <div class="lang-row">
                    <div class="lang-select-wrap">
                        <div class="lang-label">From Language</div>
                        <select name="src" id="srcLang">
                            <option value="auto">🌐 Auto Detect</option>
                            <option value="en">🇺🇸 English</option>
                            <option value="ur">🇵🇰 Urdu</option>
                            <option value="fr">🇫🇷 French</option>
                            <option value="es">🇪🇸 Spanish</option>
                            <option value="ar">🇸🇦 Arabic</option>
                            <option value="zh-CN">🇨🇳 Chinese</option>
                            <option value="de">🇩🇪 German</option>
                            <option value="ja">🇯🇵 Japanese</option>
                            <option value="ko">🇰🇷 Korean</option>
                            <option value="hi">🇮🇳 Hindi</option>
                            <option value="tr">🇹🇷 Turkish</option>
                            <option value="ru">🇷🇺 Russian</option>
                            <option value="it">🇮🇹 Italian</option>
                        </select>
                    </div>

                    <button type="button" class="swap-btn" onclick="swapLangs()">⇄</button>

                    <div class="lang-select-wrap">
                        <div class="lang-label">To Language</div>
                        <select name="dest" id="destLang">
                            <option value="ur">🇵🇰 Urdu</option>
                            <option value="en">🇺🇸 English</option>
                            <option value="fr">🇫🇷 French</option>
                            <option value="es">🇪🇸 Spanish</option>
                            <option value="ar">🇸🇦 Arabic</option>
                            <option value="zh-CN">🇨🇳 Chinese</option>
                            <option value="de">🇩🇪 German</option>
                            <option value="ja">🇯🇵 Japanese</option>
                            <option value="ko">🇰🇷 Korean</option>
                            <option value="hi">🇮🇳 Hindi</option>
                            <option value="tr">🇹🇷 Turkish</option>
                            <option value="ru">🇷🇺 Russian</option>
                            <option value="it">🇮🇹 Italian</option>
                        </select>
                    </div>
                </div>

                <div class="areas-row">
                    <div class="area-wrap">
                        <div class="area-label">Your Text</div>
                        <textarea name="text" placeholder="Type or paste your text here...">{{ text }}</textarea>
                    </div>
                    <div class="area-wrap">
                        <div class="area-label">Translation</div>
                        <textarea class="result-area" readonly placeholder="Translation will appear here...">{{ translated }}</textarea>
                        {% if translated %}
                        <button type="button" class="copy-btn" onclick="copyText()">Copy</button>
                        {% endif %}
                    </div>
                </div>

                <div class="btn-wrap">
                    <button type="submit" class="translate-btn">✨ Translate Now</button>
                </div>
            </form>
        </div>

        <div class="stats-row">
            <div class="stat">
                <div class="stat-num">13+</div>
                <div class="stat-label">Languages</div>
            </div>
            <div class="divider"></div>
            <div class="stat">
                <div class="stat-num">AI</div>
                <div class="stat-label">Powered</div>
            </div>
            <div class="divider"></div>
            <div class="stat">
                <div class="stat-num">100%</div>
                <div class="stat-label">Free</div>
            </div>
            <div class="divider"></div>
            <div class="stat">
                <div class="stat-num">∞</div>
                <div class="stat-label">Translations</div>
            </div>
        </div>
    </div>

    <script>
        // Floating particles
        for (let i = 0; i < 15; i++) {
            const p = document.createElement('div');
            p.className = 'particle';
            const size = Math.random() * 4 + 2;
            const colors = ['#7c3aed','#db2777','#2563eb','#a78bfa','#f472b6'];
            p.style.cssText = `
                width:${size}px; height:${size}px;
                left:${Math.random()*100}%;
                background:${colors[Math.floor(Math.random()*colors.length)]};
                animation-duration:${8+Math.random()*12}s;
                animation-delay:${Math.random()*10}s;
            `;
            document.body.appendChild(p);
        }

        // Swap languages
        function swapLangs() {
            const src = document.getElementById('srcLang');
            const dest = document.getElementById('destLang');
            const temp = src.value;
            src.value = dest.value;
            dest.value = temp;
        }

        // Copy translation
        function copyText() {
            const result = document.querySelectorAll('textarea')[1].value;
            navigator.clipboard.writeText(result);
        }

        // 3D card mouse effect
        const card = document.querySelector('.translator-card');
        card.addEventListener('mousemove', e => {
            const rect = card.getBoundingClientRect();
            const x = (e.clientX - rect.left) / rect.width - 0.5;
            const y = (e.clientY - rect.top) / rect.height - 0.5;
            card.style.transform = `perspective(1000px) rotateX(${-y*4}deg) rotateY(${x*4}deg)`;
        });
        card.addEventListener('mouseleave', () => {
            card.style.transform = 'perspective(1000px) rotateX(1deg)';
        });
    </script>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    translated = ''
    text = ''
    if request.method == 'POST':
        text = request.form['text']
        src = request.form['src']
        dest = request.form['dest']
        translated = GoogleTranslator(source=src, target=dest).translate(text)
    return render_template_string(HTML, translated=translated, text=text)

if __name__ == '__main__':
    app.run(debug=True)