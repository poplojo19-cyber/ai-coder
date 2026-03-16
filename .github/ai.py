import os, json, requests, re

def get_ai_response(system_prompt, user_prompt, groq_key):
    try:
        resp = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"},
            json={
                "model": "llama-3.1-8b-instant",
                "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
                "temperature": 0.1
            }
        )
        content = resp.json()["choices"][0]["message"]["content"]
        return content
    except Exception as e:
        print(f"API Error: {e}")
        return None

def run():
    groq_key = os.environ.get("GROQ_API_KEY")
    prompt = os.environ.get("PROMPT")

    # 1. Ask the AI what to do
    system = "You are a coding agent. Respond ONLY in this exact format:\nSTART_LINE: 1\nEND_LINE: 1\n[CODE_START]\nnew code\n[CODE_END]"
    response = get_ai_response(system, f"Task: {prompt}", groq_key)
    
    # 2. Robust Parsing with Default Values
    try:
        # Try to find the tags, if not found, default to line 1
        s_match = re.search(r'START_LINE:\s*(\d+)', response)
        s_line = int(s_match.group(1)) if s_match else 1
        
        e_match = re.search(r'END_LINE:\s*(\d+)', response)
        e_line = int(e_match.group(1)) if e_match else 1
        
        code_match = re.search(r'\[CODE_START\](.*?)\[CODE_END\]', response, re.DOTALL)
        new_code = code_match.group(1).strip('\n') if code_match else response
        
        # 3. Apply to file
        # Find which file to edit (The AI will say the filename in its response or we default to index.html)
        target = "index.html"
        if "portfolio" in prompt.lower(): target = "portfolio.md"
        
        lines = []
        if os.path.exists(target):
            with open(target, 'r') as f: lines = f.read().split('\n')
        
        # Pad file if it's too short
        while len(lines) < e_line: lines.append("")
        lines[max(0, s_line-1) : e_line] = [new_code]
        
        with open(target, 'w') as f: f.write('\n'.join(lines))
        print(f"Successfully modified {target}")
            
    except Exception as e:
        print(f"Failed to parse. AI Response was: {response}")
        print(f"Error: {e}")

if __name__ == "__main__":
    run()
