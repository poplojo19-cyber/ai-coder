const logTerminal = (m) => { document.getElementById('logArea').innerHTML += `\n> ${m}`; };

document.getElementById('saveSettingsBtn').onclick = () => {
    localStorage.setItem('ghUser', document.getElementById('githubUsername').value.trim());
    localStorage.setItem('ghToken', document.getElementById('githubToken').value.trim());
    localStorage.setItem('ghRepo', document.getElementById('repoName').value.trim());
    document.getElementById('settingsModal').classList.add('hidden');
    logTerminal("Settings Saved!");
};

document.getElementById('runBtn').onclick = async () => {
    const user = localStorage.getItem('ghUser');
    const token = localStorage.getItem('ghToken');
    const repo = localStorage.getItem('ghRepo');
    const path = document.getElementById('filePath').value;
    const prompt = document.getElementById('promptInput').value;

    logTerminal("Sending command to secure backend...");

    const res = await fetch(`https://api.github.com/repos/${user}/${repo}/actions/workflows/ai.yml/dispatches`, {
        method: 'POST',
        headers: { 'Authorization': `token ${token}`, 'Accept': 'application/vnd.github.v3+json' },
        body: JSON.stringify({ ref: 'main', inputs: { file_path: path, prompt: prompt } })
    });

    if (res.ok) {
        logTerminal("✅ Backend started! Wait 30s for the edit to appear.");
    } else {
        logTerminal("❌ Error. Check your GitHub Token permissions.");
    }
};

// UI handlers for modal
document.getElementById('settingsBtn').onclick = () => document.getElementById('settingsModal').classList.remove('hidden');
document.getElementById('closeSettingsBtn').onclick = () => document.getElementById('settingsModal').classList.add('hidden');
