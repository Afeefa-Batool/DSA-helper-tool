from flask import Flask, render_template, request, jsonify
import requests
import json
import markdown
import re
import traceback

app = Flask(__name__)


OPENROUTER_API_KEY = "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"

def chat_with_ai(messages):
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        },
        data=json.dumps({
            "model": "openai/o1-preview-2024-09-12",
            "messages": messages
        })
    )
    
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        return f"Error: {response.status_code} - {response.text}"

def format_message(message):
    # Convert markdown to HTML
    html = markdown.markdown(message)
    
    # Replace code blocks with formatted div
    html = re.sub(r'<pre><code>(.*?)</code></pre>', 
                  r'<div class="code-block"><pre><code>\1</code></pre></div>', 
                  html, flags=re.DOTALL)
    
    return html

@app.route('/')
def home():
    try:
        return render_template('index.html')
    except Exception as e:
        app.logger.error(f"Error in home route: {str(e)}")
        app.logger.error(traceback.format_exc())
        return f"An error occurred: {str(e)}", 500

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        messages = data['messages']
        ai_response = chat_with_ai(messages)
        formatted_response = format_message(ai_response)
        return jsonify({'response': formatted_response})
    except Exception as e:
        app.logger.error(f"Error in chat route: {str(e)}")
        app.logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)