import os, json, requests, re

def extract_json(text):
    """An Ironclad JSON parser that fixes AI formatting mistakes."""
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if not match: return None
    s = match.group()
    
    try:
        # strict=False allows actual multiline strings (which AI loves to do)
        return json.loads(s, strict=False)
    except Exception as e:
        # FALLBACK: If the AI messed up backslashes (e.g. \w or \"), fix them automatically
        s_fixed = re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', s)
        try:
            return json.loads(s_fixed, strict=False)
        except Exception as e2:
            print(f"CRITICAL JSON ERROR: {e2}")
            print(f"RAW OUTPUT THAT CRASHED:\n{text}")
            return None

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
        resp.raise_for_status()
        return extract_json(resp.json()["choices"][0]["message"]["content"])
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

    # 1. FULL CODEBASE VISION (Safely load files up to 10,000 chars to avoid token limits)
    codebase = {}
    valid_extensions = ('.html', '.js', '.css', '.md', '.py', '.json', '.txt')
    
    for root, dirs, files in os.walk("."):
        if any(x in root for x in [".git", ".github", "__pycache__"]): continue
        for f in files:
            if f.endswith(valid_extensions):
                filepath = os.path.join(root, f).replace("./", "")
                try:
                    with open(filepath, "r") as file:
                        content = file.read()
                        if len(content) < 10000:  # Prevent massive files from crashing the AI
                            codebase[filepath] = content
                except: pass

    print(f"👁️ Scanned {len(codebase)} files. Analyzing architecture...")

    # 2. THE MASTER PLAN
    system_prompt = """You are an Autonomous AI Software Engineer.
    You will receive a dictionary of the ENTIRE codebase and a user request.
    Decide what needs to be created, modified, or deleted across multiple files.
    
    You MUST respond with a SINGLE JSON object in this EXACT format:
    {
      "thoughts": "Explain your plan.",
      "operations": [
        {
          "tool": "create" | "append" | "replace" | "delete",
          "file": "path/to/file.ext",
          "search": "If replace, put exact old code here. Else leave empty.",
          "code": "The new code."
        }
      ]
    }
    CRITICAL: Properly escape all quotes and backslashes inside your code values!"""

    user_prompt = f"CODEBASE STATE:\n{json.dumps(codebase)}\n\nUSER REQUEST: {prompt}\n\nExecute the plan."

    print("⏳ Formulating multi-step execution plan...")
    plan = call_agent(system_prompt, user_prompt, groq_key)

    if not plan or "operations" not in plan:
        print("❌ Agent failed to create a valid master plan. See logs above.")
        return

    print(f"💡 MASTER PLAN: {plan.get('thoughts', 'Executing steps...')}")
    print("--------------------------------------------------")

    # 3. THE EXECUTION LOOP
    operations = plan["operations"]
    for i, op in enumerate(operations):
        tool = op.get("tool")
        target_file = op.get("file")
        search = op.get("search", "")
        
        # Clean the code (Sometimes AI wraps it in ```css ... ``` inside the JSON)
        code = op.get("code", "")
        code = re.sub(r'^```[a-z]*\n|```$', '', code, flags=re.MULTILINE).strip('\n')
        
        print(f"[{i+1}/{len(operations)}] Executing [{tool.upper()}] on {target_file}...")

        try:
            # Auto-create directories if they don't exist
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
                        print("   ⚠️ Strict search failed. Fallback: Overwriting file.")
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
