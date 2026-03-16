import os, json, requests, re

def call_ai(system_prompt, user_prompt, groq_key):
    try:
        resp = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"},
            json={
                "model": "llama-3.1-8b-instant",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.1
            }
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Groq Error: {e}")
        return None

def extract_json(text):
    try:
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1:
            return json.loads(text[start:end+1])
        return None
    except: return None

def run():
    groq_key = os.environ.get("GROQ_API_KEY")
    prompt = os.environ.get("PROMPT")

    print("========================================")
    print(f"🚀 OPENCLAW AGENT ACTIVATED")
    print(f"Task: {prompt}")
    print("========================================")

    # 1. DISCOVERY
    all_files = [os.path.join(root, f).replace("./", "") for root, dirs, files in os.walk(".") for f in files if not any(x in root for x in [".git", ".github", "__pycache__"])]
    
    history = []
    if os.path.exists("memory.json"):
        try:
            with open("memory.json", "r") as f: history = json.load(f)
        except: pass

    # 2. PLANNING
    print("🧠 Analyzing project...")
    plan_system = """You are a Lead Software Engineer. 
    Decide WHICH single file needs to be modified or created.
    Respond ONLY with a valid JSON:
    {"file": "filename.ext", "reasoning": "Why"}"""
    
    plan_user = f"Files: {all_files}\nHistory: {history}\nTask: {prompt}"
    
    plan_response = call_ai(plan_system, plan_user, groq_key)
    plan = extract_json(plan_response)
    
    if not plan:
        print("❌ Planning Failed.")
        return

    target_file = plan["file"]
    print(f"🎯 Target: {target_file}")

    # 3. PREPARATION
    original_code = ""
    if os.path.exists(target_file):
        with open(target_file, "r") as f: original_code = f.read()
    else:
        print(f"✨ File '{target_file}' will be created.")

    # 4. EXECUTION (The Search/Replace Engine)
    print(f"✍️  Writing code for {target_file}...")
    edit_system = f"""You are an elite coding agent editing '{target_file}'.
    You MUST use a [SEARCH] and [REPLACE] block to edit the file.
    
    CRITICAL RULES:
    1. The [SEARCH] block must EXACTLY match the existing code you want to change, including indentation.
    2. The [REPLACE] block contains the new updated code.
    3. If you are creating a new file, or adding to the very end, leave [SEARCH] completely empty.
    
    FORMAT EXAMPLE:
    [SEARCH]
    function old() {{
      return 1;
    }}
    [REPLACE]
    function old() {{
      return 1;
    }}

    function new() {{
      return 2;
    }}
    [/REPLACE]"""

    edit_user = f"Current File Content:\n{original_code}\n\nTask: {prompt}"
    
    edit_response = call_ai(edit_system, edit_user, groq_key)
    if not edit_response:
        print("❌ Execution Failed.")
        return

    # 5. PARSING & APPLYING
    try:
        search_match = re.search(r'\[SEARCH\](.*?)\[REPLACE\]', edit_response, re.DOTALL)
        replace_match = re.search(r'\[REPLACE\](.*?)\[/REPLACE\]', edit_response, re.DOTALL)

        if not search_match or not replace_match:
            # Fallback if AI just outputs raw code for a new file
            if not os.path.exists(target_file):
                new_code = edit_response.replace('```javascript', '').replace('```', '').strip()
                with open(target_file, "w") as f: f.write(new_code)
                print(f"✅ Created {target_file}")
            else:
                print("❌ Could not find [SEARCH] and [REPLACE] blocks.")
                print(f"AI Output: {edit_response}")
            return

        search_text = search_match.group(1).strip('\r\n')
        replace_text = replace_match.group(1).strip('\r\n')

        if not os.path.exists(target_file) or original_code.strip() == "":
            with open(target_file, "w") as f: f.write(replace_text)
            print(f"✅ Successfully wrote to {target_file}")
        elif search_text == "":
            with open(target_file, "a") as f: f.write("\n" + replace_text)
            print(f"✅ Successfully appended to {target_file}")
        else:
            if search_text in original_code:
                updated_code = original_code.replace(search_text, replace_text)
                with open(target_file, "w") as f: f.write(updated_code)
                print(f"✅ Successfully updated {target_file}")
            else:
                print("⚠️ Strict SEARCH failed. Attempting fallback replace...")
                updated_code = original_code.replace(search_text.strip(), replace_text)
                with open(target_file, "w") as f: f.write(updated_code)
                print(f"✅ Fallback applied to {target_file}")

        # Update Memory
        history.append({"task": prompt, "file": target_file})
        with open("memory.json", "w") as f: json.dump(history[-10:], f, indent=2)

    except Exception as e:
        print(f"❌ Failed to apply edit. Error: {e}")
        print(f"AI Output:\n{edit_response}")

if __name__ == "__main__":
    run()
