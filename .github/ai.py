import os, requests, re

def call_agent(system_prompt, user_prompt, groq_key):
    try:
        resp = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"},
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
                "temperature": 0.1
            }
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"API Error: {e}")
        return None

def clean_code(text):
    """Strips markdown backticks and extreme whitespace."""
    text = re.sub(r'^```[a-z]*\n|```$', '', text.strip(), flags=re.MULTILINE)
    return text.strip()

def run():
    groq_key = os.environ.get("GROQ_API_KEY")
    prompt = os.environ.get("PROMPT")
    
    print("==================================================")
    print("🚀 OPENCLAW V3: UNIVERSAL PARSER ACTIVE")
    print("==================================================")

    # 1. READ CODEBASE
    codebase = {}
    for root, dirs, files in os.walk("."):
        if any(x in root for x in [".git", ".github", "__pycache__"]): continue
        for f in files:
            if f.endswith(('.html', '.js', '.css', '.md', '.json', '.txt')):
                filepath = os.path.join(root, f).replace("./", "")
                try:
                    with open(filepath, "r") as file: codebase[filepath] = file.read()
                except: pass

    # 2. PROMPT
    system_prompt = """You are an Elite Engineer. Design beautiful UIs with Tailwind CSS.
    Use this format for edits:
    File: filename
    <<<<
    Old code
    ====
    New code
    >>>>"""

    codebase_str = "\n".join([f"--- {f} ---\n{c}" for f, c in codebase.items()])
    plan_text = call_agent(system_prompt, f"CODE:\n{codebase_str}\n\nTASK: {prompt}", groq_key)

    if not plan_text: return

    # 3. UNIVERSAL PARSER (Handles 4 or 5 arrows, with or without backticks)
    # This regex looks for: Filename -> Arrows -> Search -> Arrows -> Replace -> Arrows
    pattern = r'(?:File:\s*)?([a-zA-Z0-9._/-]+)\s*\n+<{4,}\n(.*?)\n+={4,}\n(.*?)\n+>{4,}'
    blocks = re.finditer(pattern, plan_text, re.DOTALL)
    
    executed = False
    for match in blocks:
        executed = True
        target_file = match.group(1).strip()
        search_block = clean_code(match.group(2))
        replace_block = clean_code(match.group(3))
        
        print(f"✂️  Targeting: {target_file}")
        
        try:
            if "/" in target_file: os.makedirs(os.path.dirname(target_file), exist_ok=True)
            
            # If new file or search block is empty
            if not os.path.exists(target_file) or not search_block:
                with open(target_file, "w") as f: f.write(replace_block)
                print("   ✅ Created/Written.")
                continue
            
            with open(target_file, "r") as f: current_content = f.read()
            
            if search_block in current_content:
                new_content = current_content.replace(search_block, replace_block)
                with open(target_file, "w") as f: f.write(new_content)
                print("   ✅ Surgical Replace successful.")
            elif search_block.replace(" ", "").replace("\n", "") in current_content.replace(" ", "").replace("\n", ""):
                # Fuzzy match for whitespace/newline issues
                print("   ⚠️ Search failed precisely, attempting fuzzy match...")
                # Simple fallback: find start of search block and end of search block
                # For safety in this version, we will just overwrite if fuzzy match is needed
                with open(target_file, "w") as f: f.write(replace_block)
                print("   ✅ Fuzzy match/Overwrite successful.")
            else:
                print("   ❌ Search block not found. AI likely hallucinated original code.")
        except Exception as e:
            print(f"   ❌ Error: {e}")

    if not executed:
        print(f"⚠️ No blocks found. Raw AI text was:\n{plan_text}")

if __name__ == "__main__":
    run()
