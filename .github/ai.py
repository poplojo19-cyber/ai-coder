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
        # Extract only the JSON tool command
        match = re.search(r'\{.*\}', content, re.DOTALL)
        return json.loads(match.group()) if match else None
    except Exception as e:
        print(f"Agent Error: {e}")
        return None

def run():
    groq_key = os.environ.get("GROQ_API_KEY")
    prompt = os.environ.get("PROMPT")
    
    print("🤖 GITHUB COPILOT AGENT ACTIVATED")

    # 1. SCAN THE ENVIRONMENT
    all_files = [os.path.join(r, f).replace("./", "") for r, d, fs in os.walk(".") for f in fs if not any(x in r for x in [".git", ".github", "__pycache__"])]

    # 2. DECIDE TARGET
    target_plan = call_agent(
        "You are an AI planner. Return ONLY JSON: {'file': 'target_filename'}",
        f"Files: {all_files}\nTask: {prompt}",
        groq_key
    )
    if not target_plan: return
    target_file = target_plan.get("file", "index.html")
    print(f"🎯 Target Acquired: {target_file}")

    # Read current file state
    current_content = ""
    if os.path.exists(target_file):
        with open(target_file, "r") as f: current_content = f.read()

    # 3. SELECT A WEAPON/TOOL
    tool_system = """You are an advanced GitHub Agent equipped with 3 tools:
    1. "create" -> Creates a new file.
    2. "append" -> Adds code to the bottom of an existing file.
    3. "replace" -> Replaces a specific block of existing code.

    You MUST respond with a JSON Tool Call:
    {
      "tool": "create" | "append" | "replace",
      "search": "If replacing, put the EXACT old code here. Otherwise leave empty.",
      "code": "The new code to inject or create"
    }"""

    tool_user = f"File: {target_file}\n\nCURRENT CONTENT:\n{current_content}\n\nTASK: {prompt}\nSelect your tool."
    
    action = call_agent(tool_system, tool_user, groq_key)
    if not action:
        print("❌ Agent failed to select a tool.")
        return

    # 4. EXECUTE THE TOOL IN PYTHON (The "Weapon" firing)
    tool = action.get("tool")
    search = action.get("search", "")
    code = action.get("code", "")

    try:
        if tool == "create":
            with open(target_file, "w") as f: f.write(code)
            print(f"✅ TOOL USED: [CREATE] -> Successfully built {target_file}")
            
        elif tool == "append":
            with open(target_file, "a") as f: f.write("\n" + code)
            print(f"✅ TOOL USED: [APPEND] -> Safely injected code into {target_file}")
            
        elif tool == "replace":
            if search in current_content:
                new_content = current_content.replace(search, code)
                with open(target_file, "w") as f: f.write(new_content)
                print(f"✅ TOOL USED: [REPLACE] -> Surgically swapped code in {target_file}")
            else:
                print("⚠️ TOOL MISFIRE: [REPLACE] failed. The AI couldn't find the exact 'search' text.")
                print(f"AI searched for:\n{search}")
                
        else:
            print(f"❌ Unknown tool selected: {tool}")

    except Exception as e:
        print(f"❌ Execution crash: {e}")

if __name__ == "__main__":
    run()
