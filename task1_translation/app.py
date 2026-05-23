from flask import Flask, render_template_string, request
from deep_translator import GoogleTranslator

app = Flask(__name__)

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Language Translator</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }
        h1 { color: #333; }
        textarea { width: 100%; height: 100px; margin: 10px 0; padding: 10px; font-size: 14px; }
        select, button { padding: 10px 20px; margin: 5px; font-size: 14px; }
        button { background: #4CAF50; color: white; border: none; cursor: pointer; border-radius: 5px; }
        .result { background: #f0f0f0; padding: 15px; border-radius: 5px; margin-top: 20px; }
    </style>
</head>
<body>
    <h1>🌍 Language Translation Tool</h1>
    <form method="POST">
        <textarea name="text" placeholder="Enter text to translate...">{{ text }}</textarea>
        <br>
        <label>Source Language:</label>
        <select name="src">
            <option value="auto">Auto Detect</option>
            <option value="en">English</option>
            <option value="ur">Urdu</option>
            <option value="fr">French</option>
            <option value="es">Spanish</option>
            <option value="ar">Arabic</option>
            <option value="zh-CN">Chinese</option>
            <option value="de">German</option>
        </select>
        <label>Target Language:</label>
        <select name="dest">
            <option value="ur">Urdu</option>
            <option value="en">English</option>
            <option value="fr">French</option>
            <option value="es">Spanish</option>
            <option value="ar">Arabic</option>
            <option value="zh-CN">Chinese</option>
            <option value="de">German</option>
        </select>
        <br><br>
        <button type="submit">Translate</button>
    </form>
    {% if translated %}
    <div class="result">
        <strong>Translated Text:</strong>
        <p>{{ translated }}</p>
    </div>
    {% endif %}
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