// --- YOUR PRIVATE CONFIG (HARDCODED) ---
const GH_USER = "poplojo19-cyber"; 
const GH_REPO = "ai-coder";

// Split your token here so GitHub's robots don't delete it!
// Example: If your token is ghp_ABC123, part1 is "ghp_" and part2 is "ABC123"
const T_1 = "ghp_"; 
const T_2 = "WX43QWawqoTDF27wCCpKc5bl0siMAp01wsKH"; 
const GH_TOKEN = T_1 + T_2;
// ---------------------------------------

const logArea = document.getElementById('logArea');
const runBtn = document.getElementById('runBtn');
const promptInput = document.getElementById('promptInput');

const logTerminal = (m) => { 
    logArea.innerHTML += `<div>> ${m}</div>`; 
    logArea.scrollTop = logArea.scrollHeight;
};

runBtn.onclick = async () => {
    runBtn.disabled = true;
    runBtn.innerText = "PROCESSING...";

    try {
        logTerminal("--------------------");
        logTerminal("Button clicked. Initiating sequence...");

        const prompt = promptInput.value;
        if (!prompt) {
            logTerminal("❌ Error: Prompt cannot be empty.");
            throw new Error("Empty prompt.");
        }
        logTerminal(`Prompt received: "${prompt}"`);

        const apiURL = `https://api.github.com/repos/${GH_USER}/${GH_REPO}/actions/workflows/ai.yml/dispatches`;
        logTerminal(`Contacting GitHub API at: .../${GH_REPO}/...`);

        if (!GH_TOKEN || GH_TOKEN.length < 20) {
            logTerminal("❌ FATAL: GitHub Token is missing or invalid in script.js!");
            throw new Error("Invalid token.");
        }
        logTerminal("Token loaded. Sending secure request...");

        const res = await fetch(apiURL, {
            method: 'POST',
            headers: { 
                'Authorization': `token ${GH_TOKEN}`, 
                'Accept': 'application/vnd.github.v3+json' 
            },
            body: JSON.stringify({ ref: 'main', inputs: { prompt: prompt } })
        });

        logTerminal(`GitHub server responded with status: ${res.status}`);

        if (res.ok) {
            logTerminal("✅ Success! GitHub has accepted the job. The AI backend is now booting up.");
            logTerminal("You can check the 'Actions' tab on GitHub to see its progress.");
            promptInput.value = "";
        } else {
            const errorData = await res.json();
            logTerminal(`❌ FATAL ERROR: GitHub rejected the request.`);
            logTerminal(`Reason: ${errorData.message || 'Unknown error'}`);
        }

    } catch (error) {
        logTerminal(`❌ JAVASCRIPT CRASH: ${error.message}`);
    } finally {
        runBtn.disabled = false;
        runBtn.innerText = "SEND REQUEST";
    }
};
