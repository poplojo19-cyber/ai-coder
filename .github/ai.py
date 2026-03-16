import os, json, requests, re

def extract_json(text):
    """Bulletproof JSON extractor to prevent AI formatting crashes."""
    # Remove markdown code block syntax
    text = re.sub(r'```[a-zA-Z]*\n', '', text)
    text = re.sub(r'```', '', text)
    
    start = text.find('{')
    end = text.rfind('}')
    if start == -1 or end == -1: return None
    
    json_str = text[start:end+1]
    # Auto-fix bad backslashes (e.g., regex inside JS code)
    json_str = re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', json_str)
    
    try:
        return json.loads(json_str, strict=False)
    except Exception as e:
        print(f"JSON Parse Error: {e}")
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
        print(f"API Error: {e}")
        return None

def run():
    groq_key = os.environ.get("GROQ_API_KEY")
    prompt = os.environ.get("PROMPT")
    
    print("==================================================")
    print("🤖 OPENCLAW AUTONOMOUS ENGINEER ACTIVE")
    print(f"🗣️ User: '{prompt}'")
    print("==================================================")

    # 1. READ ENTIRE CODEBASE
    codebase = {}
    for root, dirs, files in os.walk("."):
        if any(x in root for x in [".git", ".github", "__pycache__"]): continue
        for f in files:
            if f.endswith(('.html', '.js', '.css', '.md', '.json')):
                filepath = os.path.join(root, f).replace("./", "")
                try:
                    with open(filepath, "r") as file:
                        codebase[filepath] = file.read()
                except: pass

    # 2. THE SENIOR ENGINEER SYSTEM PROMPT
    system_prompt = """You are an Elite Autonomous Frontend Engineer.
    You receive the current codebase and a high-level user request.
    
    YOUR RULES:
    1. AUTONOMY: You decide the architecture. If the user asks for a beautiful UI, use Tailwind CSS, modern glassmorphism, flexbox/grid, and professional colors.
    2. WEB STANDARDS: HTML elements go inside <body>. CSS goes in <head>. Scripts go at the bottom of <body>. NEVER place code outside </html>.
    3. SURGICAL EDITS: Do not rewrite entire files. Use the 'edit' action to replace specific blocks of code perfectly.
    
    RESPOND WITH THIS EXACT JSON FORMAT:
    {
      "thoughts": "Explain your architectural decisions.",
      "actions": [
        {
          "action": "create",
          "file": "path/to/new_file.ext",
          "content": "Full code for the new file"
        },
        {
          "action": "edit",
          "file": "path/to/existing_file.ext",
          "search": "EXACT block of old code to find (e.g., closing </body> tag or an existing div)",
          "replace": "The new code that will replace the search block"
        }
      ]
    }"""

    user_prompt = f"CODEBASE STATE:\n{json.dumps(codebase)}\n\nUSER REQUEST: {prompt}\n\nExecute the plan."

    print("🧠 Analyzing codebase and formulating architecture...")
    plan = call_agent(system_prompt, user_prompt, groq_key)

    if not plan or "actions" not in plan:
        print("❌ Agent failed to generate a valid architecture plan.")
        return

    print(f"💡 AGENT THOUGHTS: {plan.get('thoughts', 'Executing steps...')}")
    print("--------------------------------------------------")

    # 3. EXECUTE THE ACTIONS (Surgical Modding)
    for i, act in enumerate(plan["actions"]):
        action_type = act.get("action")
        target_file = act.get("file")
        
        print(f"[{i+1}/{len(plan['actions'])}] Action: {action_type.upper()} -> {target_file}")

        try:
            if "/" in target_file:
                os.makedirs(os.path.dirname(target_file), exist_ok=True)

            if action_type == "create":
                with open(target_file, "w") as f: f.write(act.get("content", ""))
                print("   ✅ File created successfully.")
                
            elif action_type == "edit":
                search_text = act.get("search", "")
                replace_text = act.get("replace", "")
                
                if os.path.exists(target_file):
                    with open(target_file, "r") as f: current_code = f.read()
                    
                    if search_text in current_code:
                        updated_code = current_code.replace(search_text, replace_text)
                        with open(target_file, "w") as f: f.write(updated_code)
                        print("   ✅ Surgical block replacement successful.")
                    else:
                        print("   ⚠️ Search block not found precisely. Using fallback intelligent replace...")
                        # Fallback: ignore leading/trailing whitespace issues
                        if search_text.strip() in current_code:
                            updated_code = current_code.replace(search_text.strip(), replace_text)
                            with open(target_file, "w") as f: f.write(updated_code)
                            print("   ✅ Fallback replacement successful.")
                        else:
                            print("   ❌ Failed to find the target code block to edit.")
                else:
                    print("   ❌ Target file does not exist.")
                    
        except Exception as e:
            print(f"   ❌ Execution error: {e}")

    print("==================================================")
    print("🎉 ALL TASKS COMPLETED")

if __name__ == "__main__":
    run()
