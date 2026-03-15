import os, json, requests, re, time

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
        return resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"AI Error: {e}")
        return None

def run():
    groq_key = os.environ.get("GROQ_API_KEY")
    prompt = os.environ.get("PROMPT")

    # 1. Discovery
    all_files = [os.path.join(root, file).replace("./", "") for root, dirs, files in os.walk(".") if not any(x in root for x in [".git", ".github", "__pycache__"])]
    print(f"I see these files: {all_files}")

    # 2. Memory
    history = []
    if os.path.exists("memory.json"):
        with open("memory.json", "r") as f:
            try: history = json.load(f)
            except: history = []

    # 3. Planning (Thinking)
    planner_system = f"You are an AI Coding Agent. Project files: {all_files}. History: {history}"
    planner_user = f"Task: '{prompt}'. Which file should I modify? Respond ONLY with JSON: {{\"file\": \"filename\", \"thought\": \"your reasoning\"}}"
    
    plan_text = get_ai_response(planner_system, planner_user, groq_key)
    print(f"AI THOUGHTS: {plan_text}")
    
    try:
        plan = json.loads(re.search(r'\{.*\}', plan_text, re.DOTALL).group())
        target_file = plan["file"]
        print(f"I have decided to edit: {target_file}")
    except Exception as e:
        print(f"Planning failed: {e}")
        return

    # 4. Execution
    original_code = ""
    if os.path.exists(target_file):
        with open(target_file, "r") as f: original_code = f.read()
    
    numbered_code = '\n'.join([f"{i+1}: {line}" for i, line in enumerate(original_code.split('\n'))])

    editor_system = f"You are editing '{target_file}'. Respond in this EXACT format:\nSTART_LINE: 1\nEND_LINE: 1\n[CODE_START]\nnew code\n[CODE_END]"
    editor_user = f"Current Content:\n{numbered_code}\n\nGoal: {prompt}"

    edit_resp = get_ai_response(editor_system, editor_user, groq_key)
    print(f"AI THOUGHTS (Editing): {edit_resp}")

    # 5. Parsing & Applying
    try:
        s_line = int(re.search(r'START_LINE:\s*(\d+)', edit_resp).group(1))
        e_line = int(re.search(r'END_LINE:\s*(\d+)', edit_resp).group(1))
        new_code = re.search(r'\[CODE_START\](.*?)\[CODE_END\]', edit_resp, re.DOTALL).group(1).strip('\n')
        
        lines = original_code.split('\n')
        # Ensure we don't go out of bounds for new files
        if not lines or lines == ['']: lines = []
        
        lines[max(0, s_line-1) : e_line] = [new_code]

        with open(target_file, "w") as f: f.write('\n'.join(lines))
        print(f"Successfully modified {target_file}")
        
        # 6. Save Memory
        history.append({"task": prompt, "file": target_file})
        with open("memory.json", "w") as f: json.dump(history[-5:], f)
            
    except Exception as e:
        print(f"Failed to apply: {e}")

if __name__ == "__main__":
    run()
