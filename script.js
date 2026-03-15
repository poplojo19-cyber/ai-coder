// DOM Elements
const settingsBtn = document.getElementById('settingsBtn');
const settingsModal = document.getElementById('settingsModal');
const closeSettingsBtn = document.getElementById('closeSettingsBtn');
const saveSettingsBtn = document.getElementById('saveSettingsBtn');
const runBtn = document.getElementById('runBtn');
const logArea = document.getElementById('logArea');

// Inputs
const githubUsernameInput = document.getElementById('githubUsername');
const githubTokenInput = document.getElementById('githubToken');
const groqKeyInput = document.getElementById('groqKey');
const repoNameInput = document.getElementById('repoName');
const filePathInput = document.getElementById('filePath');
const promptInput = document.getElementById('promptInput');

// Helper: Add text to terminal
function logTerminal(message) {
    const time = new Date().toLocaleTimeString();
    logArea.innerHTML += `\n<span class="text-gray-500">[${time}]</span> ${message}`;
    logArea.scrollTop = logArea.scrollHeight; // Auto-scroll to bottom
}

// Helper: Handle Base64 Encoding/Decoding for GitHub API
function b64DecodeUnicode(str) {
    return decodeURIComponent(atob(str).split('').map(function(c) {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
    }).join(''));
}
function b64EncodeUnicode(str) {
    return btoa(encodeURIComponent(str).replace(/%([0-9A-F]{2})/g,
        function toSolidBytes(match, p1) {
            return String.fromCharCode('0x' + p1);
    }));
}

// Load keys from LocalStorage on boot
window.onload = () => {
    githubUsernameInput.value = localStorage.getItem('githubUsername') || '';
    githubTokenInput.value = localStorage.getItem('githubToken') || '';
    groqKeyInput.value = localStorage.getItem('groqKey') || '';
    repoNameInput.value = localStorage.getItem('repoName') || '';
};

// Settings Modal Logic
settingsBtn.onclick = () => settingsModal.classList.remove('hidden');
closeSettingsBtn.onclick = () => settingsModal.classList.add('hidden');

saveSettingsBtn.onclick = () => {
    localStorage.setItem('githubUsername', githubUsernameInput.value.trim());
    localStorage.setItem('githubToken', githubTokenInput.value.trim());
    localStorage.setItem('groqKey', groqKeyInput.value.trim());
    localStorage.setItem('repoName', repoNameInput.value.trim());
    settingsModal.classList.add('hidden');
    logTerminal("✅ Settings saved securely to your device.");
};

// Main AI Logic
runBtn.onclick = async () => {
    const user = githubUsernameInput.value.trim();
    const token = githubTokenInput.value.trim();
    const groqKey = groqKeyInput.value.trim();
    const repo = repoNameInput.value.trim();
    const path = filePathInput.value.trim();
    const userPrompt = promptInput.value.trim();

    if (!user || !token || !groqKey || !repo || !path || !userPrompt) {
        logTerminal("⚠️ Error: Please fill in all fields and settings.");
        return;
    }

    runBtn.disabled = true;
    runBtn.innerText = "⏳ Processing...";

    try {
        // 1. Fetch file from GitHub
        logTerminal(`Fetching ${path} from GitHub...`);
        const ghResponse = await fetch(`https://api.github.com/repos/${user}/${repo}/contents/${path}`, {
            headers: { 'Authorization': `token ${token}` }
        });
        
        if (!ghResponse.ok) throw new Error("Could not find file on GitHub. Check path/token.");
        
        const ghData = await ghResponse.json();
        const fileSha = ghData.sha;
        const originalCode = b64DecodeUnicode(ghData.content);
        
        // Add line numbers for the AI to understand where to edit
        const lines = originalCode.split('\n');
        const numberedCode = lines.map((line, i) => `${i + 1}: ${line}`).join('\n');

        // 2. Ask Groq (Llama-3) for the modification
        logTerminal("Asking Groq (Llama-3) for code modifications...");
        const systemPrompt = `You are an expert AI coder. The user wants to modify a file.
        Here is the original file with line numbers:
        <file>
        ${numberedCode}
        </file>
        
        Based on the user's prompt, determine exactly which lines to replace.
        You must ONLY output a JSON object with 'start_line', 'end_line', and 'new_code'. 
        Do NOT wrap the JSON in markdown formatting or backticks. Just pure JSON.
        Example: {"start_line": 5, "end_line": 5, "new_code": "<h1>Updated Header</h1>"}`;

        const groqResponse = await fetch('https://api.groq.com/openai/v1/chat/completions', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${groqKey}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                model: "llama-3.1-8b-instant", // Upgraded to 3.1
                messages: [
                    { role: "system", content: systemPrompt },
                    { role: "user", content: userPrompt }
                ],
                temperature: 0.1
            })
        });

        if (!groqResponse.ok) {
    const errData = await groqResponse.json();
    throw new Error(`Groq Error: ${errData.error?.message || 'Unknown Error'}`);
}
        
        const groqData = await groqResponse.json();
        let aiOutput = groqData.choices[0].message.content;
        
        // Clean up markdown just in case the AI ignored instructions
        aiOutput = aiOutput.replace(/```json/g, '').replace(/```/g, '').trim();
        const changes = JSON.parse(aiOutput);
        
        logTerminal(`🤖 Groq suggests replacing lines ${changes.start_line} to ${changes.end_line}.`);

        // 3. Apply changes locally
        // Arrays are 0-indexed, line numbers are 1-indexed
        lines.splice(changes.start_line - 1, (changes.end_line - changes.start_line) + 1, changes.new_code);
        const updatedCode = lines.join('\n');

        // 4. Push updated code back to GitHub
        logTerminal("Pushing updated code to GitHub...");
        const pushResponse = await fetch(`https://api.github.com/repos/${user}/${repo}/contents/${path}`, {
            method: 'PUT',
            headers: {
                'Authorization': `token ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: `🤖 AI Coder Update via Groq: ${userPrompt}`,
                content: b64EncodeUnicode(updatedCode),
                sha: fileSha
            })
        });

        if (!pushResponse.ok) throw new Error("Failed to push changes to GitHub.");

        logTerminal("🎉 SUCCESS! Code modified and committed.");
        promptInput.value = ""; // Clear the prompt

    } catch (error) {
        logTerminal(`❌ Error: ${error.message}`);
    } finally {
        runBtn.disabled = false;
        runBtn.innerText = "🚀 Modify Code";
    }
};
