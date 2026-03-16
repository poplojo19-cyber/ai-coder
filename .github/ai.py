import os, json, requests, re

def run():
    groq_key = os.environ.get("GROQ_API_KEY")
    prompt = os.environ.get("PROMPT")

    # STRICT: The AI must be told not to use terminal commands
    system = """You are a file editor. 
    1. If the user asks for a new file, just write the content and set the filename.
    2. NEVER use terminal commands like 'touch' or 'mkdir'.
    3. You must use this format:
    START_LINE: 1
    END_LINE: 1
    [CODE_START]
    (file content here)
    [CODE_END]"""

    # We tell the AI clearly which file we want if it mentioned it
    user_msg = f"Task: {prompt}. If a filename is implied, use it. Output format is strict."

    resp = requests.post("https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"},
        json={"model": "llama-3.1-8b-instant", "messages": [{"role": "system", "content": system}, {"role": "user", "content": user_msg}], "temperature": 0.1})
    
    ai_resp = resp.json()["choices"][0]["message"]["content"]
    
    try:
        # Regex to find the filename if the AI provides one
        file_match = re.search(r'FILE:\s*(\S+)', ai_resp)
        target = file_match.group(1) if file_match else "index.html"
        
        # Extract code
        code_match = re.search(r'\[CODE_START\](.*?)\[CODE_END\]', ai_resp, re.DOTALL)
        new_code = code_match.group(1).strip('\n') if code_match else ai_resp
        
        # Apply to file
        lines = []
        if os.path.exists(target):
            with open(target, 'r') as f: lines = f.read().split('\n')
        
        lines[0:1] = [new_code] # Overwrite or create
        
        with open(target, 'w') as f: f.write('\n'.join(lines))
        print(f"Successfully wrote to {target}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run()
