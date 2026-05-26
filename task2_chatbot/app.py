from flask import Flask, render_template_string, request
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from faqs import faqs

app = Flask(__name__)

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>AI Chatbot</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            min-height: 100vh;
            background: #030008;
            font-family: Arial, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 20px;
            overflow: hidden;
        }

        /* Animated background */
        .bg-animate {
            position: fixed;
            top: 0; left: 0;
            width: 100%; height: 100%;
            pointer-events: none;
            z-index: 0;
        }

        .hex {
            position: absolute;
            border: 1px solid rgba(34,211,238,0.08);
            transform: rotate(30deg);
            animation: hexPulse 6s ease-in-out infinite;
        }

        @keyframes hexPulse {
            0%, 100% { opacity: 0.3; transform: rotate(30deg) scale(1); }
            50% { opacity: 0.8; transform: rotate(30deg) scale(1.05); }
        }

        .glow-orb {
            position: fixed;
            border-radius: 50%;
            filter: blur(100px);
            pointer-events: none;
            opacity: 0.12;
        }

        .orb1 { width: 600px; height: 600px; background: #06b6d4; top: -200px; left: -200px; animation: orbMove 10s ease-in-out infinite; }
        .orb2 { width: 400px; height: 400px; background: #8b5cf6; bottom: -100px; right: -100px; animation: orbMove 8s ease-in-out infinite reverse; }

        @keyframes orbMove {
            0%, 100% { transform: translate(0,0); }
            50% { transform: translate(30px, 20px); }
        }

        /* Scanline effect */
        .scanlines {
            position: fixed;
            top: 0; left: 0;
            width: 100%; height: 100%;
            background: repeating-linear-gradient(
                0deg,
                transparent,
                transparent 2px,
                rgba(0,0,0,0.08) 2px,
                rgba(0,0,0,0.08) 4px
            );
            pointer-events: none;
            z-index: 0;
        }

        .content {
            position: relative;
            z-index: 1;
            width: 100%;
            max-width: 750px;
            height: 100vh;
            max-height: 850px;
            display: flex;
            flex-direction: column;
        }

        /* Header */
        .header {
            text-align: center;
            padding: 20px 0 16px;
        }

        .status-bar {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            margin-bottom: 12px;
        }

        .status-dot {
            width: 8px; height: 8px;
            background: #22d3ee;
            border-radius: 50%;
            box-shadow: 0 0 10px #22d3ee;
            animation: blink 2s infinite;
        }

        @keyframes blink {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.3; }
        }

        .status-text {
            font-size: 0.7rem;
            color: #22d3ee;
            letter-spacing: 3px;
            text-transform: uppercase;
        }

        h1 {
            font-size: 2rem;
            font-weight: 900;
            background: linear-gradient(135deg, #22d3ee, #8b5cf6, #ec4899);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 4px;
        }

        .header-sub {
            font-size: 0.7rem;
            color: #374151;
            letter-spacing: 3px;
            text-transform: uppercase;
        }

        /* Chat window */
        .chat-window {
            flex: 1;
            background: rgba(255,255,255,0.02);
            border: 1px solid rgba(34,211,238,0.1);
            border-radius: 20px;
            padding: 20px;
            overflow-y: auto;
            margin: 10px 0;
            display: flex;
            flex-direction: column;
            gap: 16px;
            box-shadow:
                inset 0 0 60px rgba(0,0,0,0.3),
                0 0 40px rgba(34,211,238,0.05);
            scrollbar-width: thin;
            scrollbar-color: rgba(34,211,238,0.2) transparent;
        }

        .chat-window::-webkit-scrollbar { width: 4px; }
        .chat-window::-webkit-scrollbar-thumb { background: rgba(34,211,238,0.2); border-radius: 2px; }

        /* Messages */
        .msg-row {
            display: flex;
            align-items: flex-end;
            gap: 10px;
        }

        .msg-row.user { flex-direction: row-reverse; }

        .avatar {
            width: 34px; height: 34px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1rem;
            flex-shrink: 0;
        }

        .bot-avatar {
            background: linear-gradient(135deg, #06b6d4, #8b5cf6);
            box-shadow: 0 0 15px rgba(34,211,238,0.3);
        }

        .user-avatar {
            background: linear-gradient(135deg, #ec4899, #8b5cf6);
            box-shadow: 0 0 15px rgba(236,72,153,0.3);
        }

        .bubble {
            max-width: 75%;
            padding: 14px 18px;
            border-radius: 16px;
            font-size: 0.92rem;
            line-height: 1.6;
            position: relative;
        }

        .bot-bubble {
            background: rgba(6,182,212,0.08);
            border: 1px solid rgba(6,182,212,0.15);
            color: #e5e7eb;
            border-bottom-left-radius: 4px;
        }

        .user-bubble {
            background: rgba(139,92,246,0.12);
            border: 1px solid rgba(139,92,246,0.2);
            color: #e5e7eb;
            border-bottom-right-radius: 4px;
        }

        .bubble-time {
            font-size: 0.65rem;
            color: #4b5563;
            margin-top: 6px;
        }

        .bot-name {
            font-size: 0.65rem;
            color: #22d3ee;
            letter-spacing: 2px;
            text-transform: uppercase;
            margin-bottom: 4px;
        }

        .user-name {
            font-size: 0.65rem;
            color: #ec4899;
            letter-spacing: 2px;
            text-transform: uppercase;
            margin-bottom: 4px;
            text-align: right;
        }

        /* Typing indicator */
        .typing {
            display: flex;
            gap: 4px;
            padding: 14px 18px;
            background: rgba(6,182,212,0.06);
            border: 1px solid rgba(6,182,212,0.1);
            border-radius: 16px;
            border-bottom-left-radius: 4px;
            width: fit-content;
        }

        .typing span {
            width: 6px; height: 6px;
            background: #22d3ee;
            border-radius: 50%;
            animation: typingDot 1.2s infinite;
        }

        .typing span:nth-child(2) { animation-delay: 0.2s; }
        .typing span:nth-child(3) { animation-delay: 0.4s; }

        @keyframes typingDot {
            0%, 100% { transform: translateY(0); opacity: 0.4; }
            50% { transform: translateY(-6px); opacity: 1; }
        }

        /* Quick questions */
        .quick-questions {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
            padding: 8px 0;
        }

        .quick-btn {
            background: rgba(34,211,238,0.06);
            border: 1px solid rgba(34,211,238,0.15);
            border-radius: 20px;
            color: #22d3ee;
            padding: 6px 14px;
            font-size: 0.75rem;
            cursor: pointer;
            transition: all 0.2s;
            white-space: nowrap;
        }

        .quick-btn:hover {
            background: rgba(34,211,238,0.12);
            box-shadow: 0 0 15px rgba(34,211,238,0.15);
        }

        /* Input area */
        .input-area {
            padding: 12px 0 8px;
        }

        .input-row {
            display: flex;
            gap: 10px;
            align-items: center;
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(34,211,238,0.12);
            border-radius: 16px;
            padding: 8px 8px 8px 18px;
            transition: all 0.3s;
        }

        .input-row:focus-within {
            border-color: rgba(34,211,238,0.35);
            box-shadow: 0 0 25px rgba(34,211,238,0.08);
        }

        input[type=text] {
            flex: 1;
            background: none;
            border: none;
            outline: none;
            color: white;
            font-size: 0.95rem;
            padding: 8px 0;
        }

        input[type=text]::placeholder { color: #374151; }

        .send-btn {
            width: 42px; height: 42px;
            background: linear-gradient(135deg, #06b6d4, #8b5cf6);
            border: none;
            border-radius: 12px;
            color: white;
            font-size: 1rem;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s;
            box-shadow: 0 0 20px rgba(6,182,212,0.3);
            flex-shrink: 0;
        }

        .send-btn:hover {
            transform: scale(1.05);
            box-shadow: 0 0 30px rgba(6,182,212,0.5);
        }

        .send-btn:active { transform: scale(0.95); }

        .powered-by {
            text-align: center;
            font-size: 0.65rem;
            color: #1f2937;
            letter-spacing: 2px;
            text-transform: uppercase;
            padding-bottom: 8px;
        }
    </style>
</head>
<body>
    <div class="glow-orb orb1"></div>
    <div class="glow-orb orb2"></div>
    <div class="scanlines"></div>

    <div class="content">
        <div class="header">
            <div class="status-bar">
                <div class="status-dot"></div>
                <span class="status-text">Neural Network Online</span>
            </div>
            <h1>🤖 CodeAlpha AI</h1>
            <p class="header-sub">Intelligent FAQ Assistant · Always Online</p>
        </div>

        <div class="chat-window" id="chatWindow">
            <!-- Welcome message -->
            <div class="msg-row">
                <div class="avatar bot-avatar">🤖</div>
                <div>
                    <div class="bot-name">CodeAlpha AI</div>
                    <div class="bubble bot-bubble">
                        Hello! I'm your AI assistant for the CodeAlpha internship. I can answer all your questions about tasks, certificates, submissions, and more. How can I help you today?
                        <div class="bubble-time">Just now</div>
                    </div>
                </div>
            </div>

            <!-- Quick questions -->
            <div class="quick-questions">
                <button class="quick-btn" onclick="askQuestion('What is CodeAlpha?')">What is CodeAlpha?</button>
                <button class="quick-btn" onclick="askQuestion('How many tasks do I need to complete?')">Tasks required?</button>
                <button class="quick-btn" onclick="askQuestion('What certificate will I receive?')">Certificate info</button>
                <button class="quick-btn" onclick="askQuestion('Where do I submit my tasks?')">How to submit?</button>
            </div>

            {% if user_input %}
            <!-- User message -->
            <div class="msg-row user">
                <div class="avatar user-avatar">👤</div>
                <div>
                    <div class="user-name">You</div>
                    <div class="bubble user-bubble">
                        {{ user_input }}
                        <div class="bubble-time">Just now</div>
                    </div>
                </div>
            </div>

            <!-- Bot response -->
            <div class="msg-row">
                <div class="avatar bot-avatar">🤖</div>
                <div>
                    <div class="bot-name">CodeAlpha AI</div>
                    <div class="bubble bot-bubble">
                        {{ answer }}
                        <div class="bubble-time">Just now</div>
                    </div>
                </div>
            </div>
            {% endif %}
        </div>

        <div class="input-area">
            <form method="POST" id="chatForm">
                <div class="input-row">
                    <input type="text" name="question" id="questionInput"
                           placeholder="Ask me anything about CodeAlpha..." autocomplete="off" autofocus>
                    <button type="submit" class="send-btn">➤</button>
                </div>
            </form>
        </div>
        <div class="powered-by">Powered by TF-IDF · Cosine Similarity · NLP</div>
    </div>

    <script>
        function askQuestion(q) {
            document.getElementById('questionInput').value = q;
            document.getElementById('chatForm').submit();
        }

        // Auto scroll to bottom
        const chatWindow = document.getElementById('chatWindow');
        chatWindow.scrollTop = chatWindow.scrollHeight;
    </script>
</body>
</html>
'''

def get_answer(user_question):
    questions = [f["question"] for f in faqs]
    questions.append(user_question)
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(questions)
    scores = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])
    best_match = scores.argmax()
    if scores[0][best_match] < 0.1:
        return "I don't have a specific answer for that. Please contact CodeAlpha directly at services@codealpha.tech or WhatsApp: +91 9336576683"
    return faqs[best_match]["answer"]

@app.route('/', methods=['GET', 'POST'])
def index():
    user_input = ''
    answer = ''
    if request.method == 'POST':
        user_input = request.form['question']
        answer = get_answer(user_input)
    return render_template_string(HTML, user_input=user_input, answer=answer)

if __name__ == '__main__':
    app.run(debug=True, port=5001)