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
        
        # LAZY PARSING: Finds only the first valid JSON object and ignores everything after
        match = re.search(r'\{[^{]*?\}', content, re.DOTALL)
        if match:
            return match.group()
        return None
    except Exception as e:
        print(f"AI/JSON Error: {e}")
        return None

def run():
    groq_key = os.environ.get("GROQ_API_KEY")
    prompt = os.environ.get("PROMPT")

    # 1. Discovery
    all_files = [os.path.join(root, f).replace("./", "") for root, dirs, files in os.walk(".") for f in files if not any(x in root for x in [".git", ".github", "__pycache__"])]
    
    # 2. Planning
    planner_system = "You are a coding agent. Respond ONLY with a single JSON object. No extra text."
    planner_user = f"Files: {all_files}. Task: '{prompt}'. Respond ONLY with: {{\"file\": \"filename\", \"thought\": \"reasoning\"}}"
    
    plan_text = get_ai_response(planner_system, planner_user, groq_key)
    if not plan_text: 
        print("Failed to get clean JSON plan.")
        return
    
    plan = json.loads(plan_text)
    target_file = plan["file"]
    print(f"Targeting: {target_file}")

    # 3. Execution (Editing) - FIXED TO CREATE FILES
    if not os.path.exists(target_file):
        print(f"File {target_file} not found. Creating it...")
        with open(target_file, 'w') as f: f.write("") # Create empty file
        original_code = ""
    else:
        with open(target_file, "r") as f: original_code = f.read()
    
    numbered_code = '\n'.join([f"{i+1}: {line}" for i, line in enumerate(original_code.split('\n'))])

    # 4. Final Parsing (Surgical extraction)
    try:
        s_line = int(re.search(r'START_LINE:\s*(\d+)', edit_resp).group(1))
        e_line = int(re.search(r'END_LINE:\s*(\d+)', edit_resp).group(1))
        new_code = re.search(r'\[CODE_START\](.*?)\[CODE_END\]', edit_resp, re.DOTALL).group(1).strip('\n')
        
        lines = original_code.split('\n')
        # Handle cases where the file might be empty
        if not lines or lines == ['']: lines = []
        
        # Apply the edit
        lines[max(0, s_line-1) : e_line] = [new_code]
        
        with open(target_file, "w") as f: f.write('\n'.join(lines))
        print(f"Successfully modified {target_file}")
            
    except Exception as e:
        print(f"Failed to apply: {e}")

if __name__ == "__main__":
    run()
