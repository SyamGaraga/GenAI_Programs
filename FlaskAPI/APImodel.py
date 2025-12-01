import os
from flask import Flask, request, jsonify, render_template_string
import openai

# Load API key from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("Please set the OPENAI_API_KEY environment variable.")

openai.api_key = OPENAI_API_KEY

app = Flask(__name__)

# A colorful, playful HTML + CSS UI delivered from Flask.
HTML = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>ColourChat — Your Creative ChatUI</title>
  <style>
    /* Fun, colorful gradient background */
    :root{
      --glass: rgba(255,255,255,0.12);
      --accent1: #ff6b6b;
      --accent2: #fdd835;
      --accent3: #6b5bff;
      --accent4: #00d4ff;
    }
    html,body{height:100%;margin:0;font-family:Inter,ui-sans-serif,system-ui,Segoe UI,Roboto,"Helvetica Neue",Arial;}
    body{
      display:flex;align-items:center;justify-content:center;
      background: radial-gradient(1200px 600px at 10% 10%, rgba(107,91,255,0.14), transparent 10%),
                  radial-gradient(1000px 500px at 90% 90%, rgba(0,212,255,0.10), transparent 15%),
                  linear-gradient(135deg, #ffefd5 0%, #fff 50%);
      padding:24px;
    }
    .card{
      width:100%; max-width:940px; border-radius:20px; padding:26px;
      background: linear-gradient(180deg, rgba(255,255,255,0.85), rgba(255,255,255,0.79));
      box-shadow: 0 10px 30px rgba(16,24,40,0.12); backdrop-filter: blur(6px);
      border: 1px solid rgba(255,255,255,0.6);
      display:grid; gap:16px;
    }
    header{display:flex;align-items:center;gap:14px;}
    .logo{
      width:66px;height:66px;border-radius:14px;
      background: linear-gradient(135deg,var(--accent3),var(--accent4));
      display:flex;align-items:center;justify-content:center;color:white;font-weight:700;
      font-size:20px; box-shadow: 0 8px 20px rgba(107,91,255,0.18);
    }
    h1{margin:0;font-size:22px;}
    p.lead{margin:0;color:#444;}
    .controls{display:flex;gap:12px;align-items:center;}
    .prompt{width:100%;min-height:120px;border-radius:12px;padding:12px;border:none;box-shadow:inset 0 1px 0 rgba(0,0,0,0.03);resize:vertical;font-size:15px;}
    .sendBtn{
      background: linear-gradient(90deg,var(--accent1),var(--accent2));
      border:none;color:white;padding:12px 18px;border-radius:12px;font-weight:700;cursor:pointer;
      box-shadow: 0 8px 18px rgba(255,107,107,0.14);
    }
    .sendBtn:disabled{opacity:0.6;cursor:default}
    .meta{display:flex;gap:12px;align-items:center;}
    .chip{background:var(--glass);padding:8px 12px;border-radius:999px;font-weight:600;font-size:13px}
    .conversation{background:linear-gradient(180deg, rgba(250,250,255,0.6), rgba(255,255,255,0.8));border-radius:12px;padding:14px;max-height:360px;overflow:auto;border:1px solid rgba(0,0,0,0.03)}
    .msg{padding:10px;margin-bottom:10px;border-radius:10px;max-width:88%}
    .user{background:linear-gradient(90deg,#fff,#f6f9ff);align-self:flex-end;margin-left:auto;border:1px solid rgba(0,0,0,0.04)}
    .assistant{background:linear-gradient(90deg,rgba(255,255,255,0.95), rgba(245,250,255,0.95));border-left:4px solid var(--accent3)}
    footer{display:flex;justify-content:space-between;align-items:center;gap:8px}
    .credits{font-size:13px;color:#666}
    /* small screens */
    @media (max-width:720px){
      .card{padding:18px}
      .logo{width:56px;height:56px;font-size:18px}
    }
  </style>
</head>
<body>
  <main class="card" role="main">
    <header>
      <div class="logo">CC</div>
      <div style="flex:1">
        <h1>ColourChat — friendly conversational demo</h1>
        <p class="lead">Type anything. Press Send. Powered by ChatGPT (OpenAI).</p>
      </div>
      <div class="meta">
        <div class="chip">Model: gpt-3.5-turbo</div>
      </div>
    </header>

    <section>
      <textarea id="prompt" class="prompt" placeholder="Ask something creative, technical, or just fun...">Hello ChatGPT — give me a friendly tip about clean code.</textarea>
      <div style="display:flex;gap:12px;align-items:center;margin-top:8px">
        <button id="send" class="sendBtn">Send →</button>
        <div style="font-size:13px;color:#555">Responses appear below. Keep prompts concise for faster replies.</div>
      </div>
    </section>

    <section class="conversation" id="conversation" aria-live="polite">
      <!-- messages injected here -->
    </section>

    <footer>
      <div class="credits">Made with care • Colourful UI</div>
      <div style="font-size:13px;color:#777">Local demo — your API key is used server-side only.</div>
    </footer>
  </main>

  <script>
    const sendBtn = document.getElementById('send');
    const promptEl = document.getElementById('prompt');
    const conv = document.getElementById('conversation');

    function appendMessage(text, who){
      const d = document.createElement('div');
      d.className = 'msg ' + (who === 'user' ? 'user' : 'assistant');
      d.innerText = text;
      conv.appendChild(d);
      conv.scrollTop = conv.scrollHeight;
    }

    async function sendPrompt(){
      const prompt = promptEl.value.trim();
      if(!prompt) return;
      appendMessage(prompt, 'user');
      sendBtn.disabled = true;
      sendBtn.innerText = 'Thinking...';

      try{
        const resp = await fetch('/api/chat', {
          method: 'POST',
          headers: {'Content-Type':'application/json'},
          body: JSON.stringify({prompt})
        });
        if(!resp.ok){
          const txt = await resp.text();
          appendMessage('Error: ' + txt, 'assistant');
        } else {
          const data = await resp.json();
          appendMessage(data.reply, 'assistant');
        }
      } catch(err){
        appendMessage('Network error: ' + err.message, 'assistant');
      } finally {
        sendBtn.disabled = false;
        sendBtn.innerText = 'Send →';
      }
    }

    sendBtn.addEventListener('click', sendPrompt);
    promptEl.addEventListener('keydown', (e) => {
      if(e.key === 'Enter' && (e.ctrlKey || e.metaKey)) sendPrompt();
    });
  </script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML)

@app.route("/api/chat", methods=["POST"])
def chat_api():
    data = request.get_json()
    if not data or "prompt" not in data:
        return jsonify({"error": "No prompt provided."}), 400

    prompt = data["prompt"]

    # Build messages for Chat API
    messages = [
        {"role": "system", "content": "You are a helpful assistant that replies concisely and politely."},
        {"role": "user", "content": prompt}
    ]

    try:
        # Use Chat Completions API
        resp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=400,
            temperature=0.8,
            top_p=0.9
        )

        # Extract assistant text
        reply = resp["choices"][0]["message"]["content"].strip()
        return jsonify({"reply": reply})

    except Exception as e:
        # Log error server-side (in production, use proper logging)
        print("OpenAI error:", e)
        return jsonify({"error": "AI service error: " + str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
