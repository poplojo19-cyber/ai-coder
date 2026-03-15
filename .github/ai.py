import os, json, requests, re

def run():
    groq_key = os.environ.get("GROQ_API_KEY")
    prompt = os.environ.get("PROMPT")

    # 1. List all files (eyes)
    all_files = []
    for root, dirs, files in os.walk("."):
        if ".git" in root or ".github" in root: continue
        for file in files:
            all_files.append(os.path.join(root, file))

    # 2. Read Memory
    history = ""
    if os.path.exists("memory.json"):
        with open("memory.json", "r") as f:
            history = f.read()

    # 3. Ask AI to pick a file and plan
    system_planner = f"""You are an advanced AI. Here is the project structure: {all_files}
    History of changes: {history}
    The user wants: {prompt}
    
    Decide which file needs to be modified. Return ONLY a JSON:
    {{"file": "filename", "reason": "why"}}"""

    resp = requests.post("https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {groq_key}"},
        json={"model": "llama-3.1-8b-instant", "messages": [{"role": "system", "content": system_planner}], "temperature": 0.1})
    
    plan = json.loads(re.search(r'\{.*\}', resp.json()["choices"][0]["message"]["content"], re.DOTALL).group())
    target_file = plan["file"]
    print(f"AI decided to edit: {target_file}")

    # 4. Read the target file
    with open(target_file, "r") as f:
        original_code = f.read()
    
    lines = original_code.split('\n')
    numbered_code = '\n'.join([f"{i+1}: {line}" for i, line in enumerate(lines)])

    # 5. Execute change
    system_editor = f"You are editing {target_file}. Return ONLY JSON with start_line, end_line, and new_code."
    resp = requests.post("https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {groq_key}"},
        json={
            "model": "llama-3.1-8b-instant",
            "messages": [
                {"role": "system", "content": system_editor},
                {"role": "user", "content": f"File:\n{numbered_code}\n\nTask: {prompt}"}
            ],
            "temperature": 0.1
        })
    
    edit = json.loads(re.search(r'\{.*\}', resp.json()["choices"][0]["message"]["content"], re.DOTALL).group())
    lines[int(edit["start_line"])-1 : int(edit["end_line"])] = [edit["new_code"]]

    # 6. Update File & Memory
    with open(target_file, "w") as f:
        f.write('\n'.join(lines))
    
    # Keep history short (last 5 changes)
    mem_data = json.loads(history)
    mem_data.append({"task": prompt, "file": target_file})
    with open("memory.json", "w") as f:
        json.dump(mem_data[-5:], f)

if __name__ == "__main__":
    run()
