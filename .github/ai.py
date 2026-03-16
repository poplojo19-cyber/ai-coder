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
        # Find the first '{' and last '}' to strip "Sure!" or "Markdown"
        content = resp.json()["choices"][0]["message"]["content"]
        match = re.search(r'\{.*\}', content, re.DOTALL)
        return match.group() if match else None
    except Exception as e:
        print(f"AI/JSON Error: {e}")
        return None

def run():
    groq_key = os.environ.get("GROQ_API_KEY")
    prompt = os.environ.get("PROMPT")

    # 1. Discovery
    all_files = [os.path.join(root, f).replace("./", "") for root, dirs, files in os.walk(".") for f in files if not any(x in root for x in [".git", ".github"])]
    print(f"I see these files: {all_files}")

    # 2. Planning (Thinking)
    planner_system = "You are a coding agent. Return ONLY raw JSON. No prefix, no suffix."
    planner_user = f"Project files: {all_files}. Task: '{prompt}'. Decide the file. Respond ONLY with JSON: {{\"file\": \"filename\", \"thought\": \"reasoning\"}}"
    
    plan_text = get_ai_response(planner_system, planner_user, groq_key)
    if not plan_text: return
    
    plan = json.loads(plan_text)
    target_file = plan["file"]
    print(f"AI THOUGHTS: {plan['thought']}")
    print(f"Targeting: {target_file}")

    # 3. Execution (Editing)
    original_code = ""
    if os.path.exists(target_file):
        with open(target_file, "r") as f: original_code = f.read()
    
    numbered_code = '\n'.join([f"{i+1}: {line}" for i, line in enumerate(original_code.split('\n'))])

    editor_system = "You are a coding tool. Respond in EXACT format:\nSTART_LINE: 1\nEND_LINE: 1\n[CODE_START]\nnew code\n[CODE_END]"
    edit_resp = get_ai_response(editor_system, f"File Content:\n{numbered_code}\n\nTask: {prompt}", groq_key)
    
    if not edit_resp: return

    # 4. Final Parsing
    try:
        s_line = int(re.search(r'START_LINE:\s*(\d+)', edit_resp).group(1))
        e_line = int(re.search(r'END_LINE:\s*(\d+)', edit_resp).group(1))
        new_code = re.search(r'\[CODE_START\](.*?)\[CODE_END\]', edit_resp, re.DOTALL).group(1).strip('\n')
        
        lines = original_code.split('\n')
        if not lines or lines == ['']: lines = []
        
        lines[max(0, s_line-1) : e_line] = [new_code]
        
        with open(target_file, "w") as f: f.write('\n'.join(lines))
        print(f"Successfully modified {target_file}")
            
    except Exception as e:
        print(f"Failed to apply: {e}")

if __name__ == "__main__":
    run()
