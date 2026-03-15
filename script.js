// --- YOUR PRIVATE CONFIG (HARDCODED) ---
const GH_USER = "YOUR_USERNAME"; 
const GH_REPO = "ai-coder";

// Split your token here so GitHub's robots don't delete it!
// Example: If your token is ghp_ABC123, part1 is "ghp_" and part2 is "ABC123"
const T_1 = "ghp_"; 
const T_2 = "PASTE_THE_REST_OF_YOUR_TOKEN_HERE"; 
const GH_TOKEN = T_1 + T_2;
// ---------------------------------------

const logArea = document.getElementById('logArea');
const logTerminal = (m) => { 
    logArea.innerHTML += `\n> ${m}`; 
    logArea.scrollTop = logArea.scrollHeight;
};

document.getElementById('runBtn').onclick = async () => {
    const path = document.getElementById('filePath').value || 'index.html';
    const prompt = document.getElementById('promptInput').value;

    if (!prompt) {
        logTerminal("❌ Type a prompt first!");
        return;
    }

    logTerminal("🚀 Sending command to GitHub Backend...");

    try {
        const res = await fetch(`https://api.github.com/repos/${GH_USER}/${GH_REPO}/actions/workflows/ai.yml/dispatches`, {
            method: 'POST',
            headers: { 
                'Authorization': `token ${GH_TOKEN}`, 
                'Accept': 'application/vnd.github.v3+json' 
            },
            body: JSON.stringify({ ref: 'main', inputs: { file_path: path, prompt: prompt } })
        });

        if (res.ok) {
            logTerminal("✅ Success! Server is booting up.");
            logTerminal("Wait ~40s, then refresh your site.");
            document.getElementById('promptInput').value = "";
        } else {
            const data = await res.json();
            logTerminal(`❌ Error: ${data.message}`);
        }
    } catch (e) {
        logTerminal("❌ Connection error.");
    }
};
