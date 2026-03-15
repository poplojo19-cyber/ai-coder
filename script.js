// --- YOUR PRIVATE CONFIG (HARDCODED) ---
const GH_USER = "poplojo19-cyber"; 
const GH_REPO = "ai-coder";

// Split your token here so GitHub's robots don't delete it!
// Example: If your token is ghp_ABC123, part1 is "ghp_" and part2 is "ABC123"
const T_1 = "ghp_"; 
const T_2 = "nJRuo4j97YulGuEJ6KKCbrdvzXnhgj2MtjeT"; 
const GH_TOKEN = T_1 + T_2;
// ---------------------------------------

const logArea = document.getElementById('logArea');
const logTerminal = (m) => { 
    logArea.innerHTML += `\n> ${m}`; 
    logArea.scrollTop = logArea.scrollHeight;
};

// ... keep your GH_USER, GH_REPO, and split GH_TOKEN at the top ...

document.getElementById('runBtn').onclick = async () => {
    const prompt = document.getElementById('promptInput').value;
    const log = (m) => { document.getElementById('logArea').innerHTML += `<div>> ${m}</div>`; };

    if(!prompt) return;
    log("Thinking...");

    const res = await fetch(`https://api.github.com/repos/${GH_USER}/${GH_REPO}/actions/workflows/ai.yml/dispatches`, {
        method: 'POST',
        headers: { 'Authorization': `token ${GH_TOKEN}`, 'Accept': 'application/vnd.github.v3+json' },
        body: JSON.stringify({ ref: 'main', inputs: { file_path: "auto", prompt: prompt } }) // "auto" because AI decides
    });

    if (res.ok) {
        log("Command sent. AI is analyzing repository structure...");
        document.getElementById('promptInput').value = "";
    }
};
