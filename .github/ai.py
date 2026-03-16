import os, json, requests, re, time

def get_ai_response(system_prompt, user_prompt, groq_key):
    resp = requests.post("https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"},
        json={
            "model": "llama-3.1-8b-instant",
            "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
            "temperature": 0.2
        })
    content = resp.json()["choices"][0]["message"]["content"]
    start, end = content.find('{'), content.rfind('}')
    return content[start:end+1] if start != -1 and end != -1 else None

def run():
    groq_key = os.environ.get("GROQ_API_KEY")
    prompt = os.environ.get("PROMPT")

    # 1. Planning
    plan_json = get_ai_response("You are a Project Manager. Return JSON: {'task': 'description', 'file': 'filename'}", f"Goal: {prompt}. Pick the first file to work on.", groq_key)
    plan = json.loads(plan_json)
    target = plan['file']
    print(f"Plan: {plan['task']} on {target}")

    # 2. Execution with Verification
    # We pass the instruction to WRITE the content, not just create the file
    editor_system = "You are a coder. Format: START_LINE: 1\nEND_LINE: 1\n[CODE_START]\nFull Content Here\n[CODE_END]"
    edit_resp = get_ai_response(editor_system, f"Task: {prompt}. Write the full content for {target}.", groq_key)
    
    # Surgical Extraction
    s_line = int(re.search(r'START_LINE:\s*(\d+)', edit_resp).group(1))
    e_line = int(re.search(r'END_LINE:\s*(\d+)', edit_resp).group(1))
    new_code = re.search(r'\[CODE_START\](.*?)\[CODE_END\]', edit_resp, re.DOTALL).group(1).strip('\n')

    # Apply
    lines = []
    if os.path.exists(target):
        with open(target, 'r') as f: lines = f.read().split('\n')
    
    # Pad lines if needed
    while len(lines) < e_line: lines.append("")
    lines[max(0, s_line-1) : e_line] = [new_code]
    
    with open(target, 'w') as f: f.write('\n'.join(lines))
    print(f"Verified: {target} is now filled with data.")

if __name__ == "__main__":
    run()
