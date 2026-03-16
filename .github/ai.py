import os, json, requests, re

def call_agent(system_prompt, user_prompt, groq_key):
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
        # Find the master JSON object
        match = re.search(r'\{.*\}', content, re.DOTALL)
        return json.loads(match.group()) if match else None
    except Exception as e:
        print(f"Agent Error: {e}")
        return None

def run():
    groq_key = os.environ.get("GROQ_API_KEY")
    prompt = os.environ.get("PROMPT")
    
    print("==================================================")
    print("🧠 OPENCLAW AUTONOMOUS ENGINEER ONLINE")
    print(f"🗣️ User Request: '{prompt}'")
    print("==================================================")

    # 1. FULL CODEBASE VISION
    # We load the actual contents of every text file into the AI's brain
    codebase = {}
    valid_extensions = ('.html', '.js', '.css', '.md', '.py', '.json', '.txt')
    
    for root, dirs, files in os.walk("."):
        if any(x in root for x in [".git", ".github", "__pycache__"]): continue
        for f in files:
            if f.endswith(valid_extensions):
                filepath = os.path.join(root, f).replace("./", "")
                try:
                    with open(filepath, "r") as file:
                        codebase[filepath] = file.read()
                except: pass

    print(f"👁️ Scanned {len(codebase)} files. Analyzing architecture...")

    # 2. THE MASTER PLAN
    system_prompt = """You are an Autonomous AI Software Engineer.
    You will receive a dictionary of the ENTIRE codebase and a vague user request.
    You must figure out what needs to be created, modified, or deleted across multiple files to achieve the goal perfectly.
    
    You MUST respond with a SINGLE JSON object in this EXACT format:
    {
      "thoughts": "Explain your master plan here...",
      "operations": [
        {
          "tool": "create" | "append" | "replace" | "delete",
          "file": "path/to/file.ext",
          "search": "If replace, put exact old code here. Else empty.",
          "code": "The new code."
        }
      ]
    }"""

    user_prompt = f"CODEBASE STATE:\n{json.dumps(codebase)}\n\nUSER REQUEST: {prompt}\n\nExecute the plan."

    print("⏳ Formulating multi-step execution plan...")
    plan = call_agent(system_prompt, user_prompt, groq_key)

    if not plan or "operations" not in plan:
        print("❌ Agent failed to create a valid master plan.")
        return

    print(f"💡 MASTER PLAN: {plan.get('thoughts', 'Executing steps...')}")
    print("--------------------------------------------------")

    # 3. THE EXECUTION LOOP
    operations = plan["operations"]
    for i, op in enumerate(operations):
        tool = op.get("tool")
        target_file = op.get("file")
        search = op.get("search", "")
        code = op.get("code", "")
        
        print(f"[{i+1}/{len(operations)}] Executing [{tool.upper()}] on {target_file}...")

        try:
            # Ensure folders exist (e.g., if AI wants to create css/style.css)
            if "/" in target_file:
                os.makedirs(os.path.dirname(target_file), exist_ok=True)

            if tool == "create":
                with open(target_file, "w") as f: f.write(code)
                print("   ✅ File created.")
                
            elif tool == "append":
                with open(target_file, "a") as f: f.write("\n" + code)
                print("   ✅ Code appended.")
                
            elif tool == "replace":
                if os.path.exists(target_file):
                    with open(target_file, "r") as f: current = f.read()
                    if search in current:
                        with open(target_file, "w") as f: f.write(current.replace(search, code))
                        print("   ✅ Surgical replace successful.")
                    else:
                        print("   ⚠️ Search text not found. Fallback: Replacing entire file.")
                        with open(target_file, "w") as f: f.write(code)
                else:
                    print("   ❌ Target file missing for replace.")
                    
            elif tool == "delete":
                if os.path.exists(target_file):
                    os.remove(target_file)
                    print("   🗑️ File deleted.")
                    
        except Exception as e:
            print(f"   ❌ Step failed: {e}")

    print("==================================================")
    print("🎉 ALL OPERATIONS COMPLETED")

if __name__ == "__main__":
    run()
