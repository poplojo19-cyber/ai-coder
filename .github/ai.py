import os, requests, re, json

def call_groq(system, user, key):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
        "temperature": 0
    }
    try:
        r = requests.post(url, headers=headers, json=data)
        return r.json()['choices'][0]['message']['content']
    except Exception as e:
        print(f"Error calling Groq: {e}")
        return None

def run():
    key = os.environ.get("GROQ_API_KEY")
    prompt = os.environ.get("PROMPT")
    
    print(f"🚀 OPENCLAW STARTING\nTask: {prompt}\n")

    # 1. SCAN FILES
    files = [f for f in os.listdir('.') if f.endswith(('.html', '.js', '.css'))]
    codebase = ""
    for f in files:
        with open(f, 'r') as content:
            codebase += f"\n--- FILE: {f} ---\n{content.read()}\n"

    # 2. ASK AI FOR EDITS
    system = "You are a GitHub File Editor. Use this format:\nFile: [name]\n<<<<\n[old code]\n====\n[new code]\n>>>>"
    print("📡 Contacting AI...")
    response = call_groq(system, f"CODEBASE:\n{codebase}\n\nUSER REQUEST: {prompt}", key)
    
    if not response:
        print("❌ No response from AI.")
        return

    print(f"--- AI RESPONSE ---\n{response}\n-------------------")

    # 3. APPLY EDITS
    # Look for: File: ... <<<< ... ==== ... >>>>
    sections = re.findall(r'File:\s*(\S+).*?<{4,}\n(.*?)\n+={4,}\n(.*?)\n+>{4,}', response, re.DOTALL)
    
    for filename, search, replace in sections:
        filename = filename.strip()
        search = search.strip('\r\n')
        replace = replace.strip('\r\n')
        
        if not os.path.exists(filename):
            with open(filename, 'w') as f: f.write(replace)
            print(f"✅ Created {filename}")
            continue

        with open(filename, 'r') as f:
            content = f.read()

        if search in content:
            new_content = content.replace(search, replace)
            with open(filename, 'w') as f: f.write(new_content)
            print(f"✅ Edited {filename} successfully.")
        else:
            print(f"❌ Could not find search block in {filename}. Check indentation!")

if __name__ == "__main__":
    run()
