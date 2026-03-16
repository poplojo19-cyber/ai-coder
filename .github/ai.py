import os, json, requests, re

def get_ai_response(system, user, groq_key):
    resp = requests.post("https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"},
        json={"model": "llama-3.1-8b-instant", "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}], "temperature": 0.1})
    return resp.json()["choices"][0]["message"]["content"]

def run():
    groq_key = os.environ.get("GROQ_API_KEY")
    prompt = os.environ.get("PROMPT")

    # 1. Discovery
    files = [os.path.join(r, f).replace("./", "") for r, _, fs in os.walk(".") for f in fs if not any(x in r for x in [".git", ".github"])]
    
    # 2. Planning (The "Native" Brain)
    # We ask the AI to decide the filename BEFORE it writes the code
    plan_system = "You are a lead developer. Output ONLY: {'file': 'filename.ext', 'thought': 'reasoning'}"
    plan_user = f"Context: {files}. User wants: '{prompt}'. Which file should I edit or create? Respond in JSON."
    
    plan_json = get_ai_response(plan_system, plan_user, groq_key)
    plan = json.loads(re.search(r'\{.*\}', plan_json, re.DOTALL).group())
    target = plan['file']
    print(f"AI decided to work on: {target}")

    # 3. Execution
    editor_system = f"You are editing {target}. Respond in EXACT format:\n[CODE_START]\n(code here)\n[CODE_END]"
    code_resp = get_ai_response(editor_system, f"Task: {prompt}. Write the full file content for {target}.", groq_key)
    
    # 4. Save
    new_code = re.search(r'\[CODE_START\](.*?)\[CODE_END\]', code_resp, re.DOTALL).group(1).strip('\n')
    
    with open(target, 'w') as f: f.write(new_code)
    print(f"Successfully saved to {target}")

if __name__ == "__main__":
    run()
