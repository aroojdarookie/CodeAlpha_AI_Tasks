from flask import Flask, render_template_string, request
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from faqs import faqs

app = Flask(__name__)

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>FAQ Chatbot</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }
        h1 { color: #333; }
        .chat-box { border: 1px solid #ddd; border-radius: 10px; padding: 20px; min-height: 300px; margin-bottom: 20px; background: #fafafa; }
        .user-msg { background: #DCF8C6; padding: 10px; border-radius: 10px; margin: 8px 0; text-align: right; }
        .bot-msg { background: #fff; border: 1px solid #ddd; padding: 10px; border-radius: 10px; margin: 8px 0; }
        input[type=text] { width: 75%; padding: 10px; font-size: 14px; border: 1px solid #ddd; border-radius: 5px; }
        button { padding: 10px 20px; background: #128C7E; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 14px; }
    </style>
</head>
<body>
    <h1>🤖 FAQ Chatbot</h1>
    <div class="chat-box">
        {% if user_input %}
        <div class="user-msg">{{ user_input }}</div>
        <div class="bot-msg"><strong>Bot:</strong> {{ answer }}</div>
        {% else %}
        <div class="bot-msg"><strong>Bot:</strong> Hi! Ask me anything about the CodeAlpha internship.</div>
        {% endif %}
    </div>
    <form method="POST">
        <input type="text" name="question" placeholder="Type your question here..." autofocus>
        <button type="submit">Send</button>
    </form>
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
        return "Sorry, I don't have an answer for that. Please contact CodeAlpha directly."
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