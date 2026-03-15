import os, json, requests, re

def run():
    # 1. Get Environment Variables
    groq_key = os.environ.get("GROQ_API_KEY")
    file_path = os.environ.get("FILE_PATH")
    prompt = os.environ.get("PROMPT")

    print(f"Targeting: {file_path}")

    # 2. Read the file
    with open(file_path, "r") as f:
        original_code = f.read()

    lines = original_code.split('\n')
    numbered_code = '\n'.join([f"{i+1}: {line}" for i, line in enumerate(lines)])

    # 3. Prompt the AI
    system_prompt = "You are a coding tool. You MUST return ONLY a JSON object. No conversation. No markdown."
    user_msg = f"In the file below, {prompt}\n\nFile:\n{numbered_code}\n\nReturn JSON: {{\"start_line\": int, \"end_line\": int, \"new_code\": str}}"

    print("Requesting Groq...")
    resp = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"},
        json={
            "model": "llama-3.1-8b-instant",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_msg}
            ],
            "temperature": 0.1
        }
    )

    if not resp.ok:
        print(f"Groq API Error: {resp.text}")
        return

    full_content = resp.json()["choices"][0]["message"]["content"]
    print(f"AI Response received. Searching for JSON...")

    # 4. TRICK: Use Regex to find the JSON block even if there is "Extra Data"
    try:
        # This finds the first { and the last } and everything in between
        json_match = re.search(r'\{.*\}', full_content, re.DOTALL)
        if json_match:
            clean_json = json_match.group()
            changes = json.loads(clean_json)
        else:
            print(f"Could not find JSON in response: {full_content}")
            return
    except Exception as e:
        print(f"JSON Parsing failed: {e}")
        print(f"Raw Content: {full_content}")
        return

    # 5. Apply the changes
    try:
        start = int(changes["start_line"]) - 1
        end = int(changes["end_line"])
        new_text = changes["new_code"]

        print(f"Modifying lines {start+1} to {end}")
        lines[start:end] = [new_text]

        with open(file_path, "w") as f:
            f.write('\n'.join(lines))
        print("Successfully updated file.")
    except Exception as e:
        print(f"Error applying changes: {e}")

if __name__ == "__main__":
    run()
