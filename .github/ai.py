import os, json, requests, re

def run():
    groq_key = os.environ.get("GROQ_API_KEY")
    prompt = os.environ.get("PROMPT")

    # Fixed File Discovery
    all_files = []
    for root, dirs, files in os.walk("."):
        if any(x in root for x in [".git", ".github", "__pycache__"]): continue
        for f in files:
            all_files.append(os.path.join(root, f).replace("./", ""))
    
    print(f"I see these files: {all_files}")

    history = []
    if os.path.exists("memory.json"):
        with open("memory.json", "r") as f:
            try: history = json.load(f)
            except: history = []

    planner_system = f"You are a coding agent. Files: {all_files}. History: {history}"
    planner_user = f"Task: '{prompt}'. Respond ONLY with JSON: {{\"file\": \"filename\", \"thought\": \"reasoning\"}}"
    
    resp = requests.post("https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"},
        json={"model": "llama-3.1-8b-instant", "messages": [{"role": "system", "content": planner_system}, {"role": "user", "content": planner_user}], "temperature": 0.1})
    
    plan = json.loads(re.search(r'\{.*\}', resp.json()["choices"][0]["message"]["content"], re.DOTALL).group())
    target_file = plan["file"]
    
    original_code = ""
    if os.path.exists(target_file):
        with open(target_file, "r") as f: original_code = f.read()
    
    numbered_code = '\n'.join([f"{i+1}: {line}" for i, line in enumerate(original_code.split('\n'))])

    editor_system = "You are editing. Respond in EXACT format:\nSTART_LINE: 1\nEND_LINE: 1\n[CODE_START]\nnew code\n[CODE_END]"
    edit_resp = requests.post("https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"},
        json={"model": "llama-3.1-8b-instant", "messages": [{"role": "system", "content": editor_system}, {"role": "user", "content": f"File:\n{numbered_code}\n\nTask: {prompt}"}], "temperature": 0.1})
    
    ai_resp = edit_resp.json()["choices"][0]["message"]["content"]
    s_line = int(re.search(r'START_LINE:\s*(\d+)', ai_resp).group(1))
    e_line = int(re.search(r'END_LINE:\s*(\d+)', ai_resp).group(1))
    new_code = re.search(r'\[CODE_START\](.*?)\[CODE_END\]', ai_resp, re.DOTALL).group(1).strip('\n')
    
    lines = original_code.split('\n')
    lines[max(0, s_line-1) : e_line] = [new_code]
    with open(target_file, "w") as f: f.write('\n'.join(lines))
        
    history.append({"task": prompt, "file": target_file})
    with open("memory.json", "w") as f: json.dump(history[-5:], f)

if __name__ == "__main__":
    run()
