// ============================================
// AI Assistant — Frontend Application Logic
// ============================================

const chatArea = document.getElementById('chatArea');
const welcomeScreen = document.getElementById('welcomeScreen');
const questionInput = document.getElementById('questionInput');
const sendBtn = document.getElementById('sendBtn');
const suggestions = document.getElementById('suggestions');
const newChatBtn = document.getElementById('newChatBtn');

let isLoading = false;

// ---------- Event Listeners ----------

sendBtn.addEventListener('click', handleSend);

questionInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    handleSend();
  }
});

if (suggestions) {
  suggestions.addEventListener('click', (e) => {
    const chip = e.target.closest('.suggestion-chip');
    if (chip) {
      const query = chip.getAttribute('data-query');
      if (query) {
        questionInput.value = query;
        handleSend();
      }
    }
  });
}

if (newChatBtn) {
  newChatBtn.addEventListener('click', resetChat);
}

// ---------- Core Chat Flow ----------

async function handleSend() {
  const question = questionInput.value.trim();
  if (!question || isLoading) return;

  // Hide welcome screen on first message
  if (welcomeScreen) {
    welcomeScreen.style.display = 'none';
  }

  // Add user message
  appendMessage('user', question);
  questionInput.value = '';
  setLoading(true);

  // Show typing indicator
  const typingEl = showTypingIndicator();

  try {
    const response = await fetch('/api/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question }),
    });

    // Remove typing indicator
    typingEl.remove();

    if (!response.ok) {
      throw new Error(`Server responded with ${response.status}`);
    }

    const data = await response.json();

    if (data.error) {
      appendError(data.error);
    } else {
      appendMessage('bot', data.answer, data.sources);
    }
  } catch (err) {
    if (typingEl && typingEl.parentNode) {
      typingEl.remove();
    }
    appendError('Unable to retrieve an answer right now. Please verify your connection or try again.');
    console.error('Search API error:', err);
  } finally {
    setLoading(false);
    questionInput.focus();
  }
}

function resetChat() {
  if (isLoading) return;
  
  // Remove all message and error elements
  const messages = chatArea.querySelectorAll('.message, .error-message, .typing-indicator');
  messages.forEach(msg => msg.remove());

  // Show welcome screen again
  if (welcomeScreen) {
    welcomeScreen.style.display = 'flex';
  }

  questionInput.value = '';
  questionInput.focus();
}

// ---------- DOM Helpers ----------

function appendMessage(role, content, sources) {
  const msg = document.createElement('div');
  msg.className = `message ${role}`;

  // Avatar Icon
  const avatar = document.createElement('div');
  avatar.className = 'message-avatar';

  if (role === 'user') {
    avatar.innerHTML = `
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"></path>
        <circle cx="12" cy="7" r="4"></circle>
      </svg>
    `;
  } else {
    avatar.innerHTML = `
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M12 8V4H8"></path>
        <rect width="16" height="12" x="4" y="8" rx="2"></rect>
        <path d="M2 14h2"></path>
        <path d="M20 14h2"></path>
        <path d="M15 13v2"></path>
        <path d="M9 13v2"></path>
      </svg>
    `;
  }

  // Wrapper for bubble and actions
  const bubbleWrapper = document.createElement('div');
  bubbleWrapper.className = 'message-bubble-wrapper';

  const bubble = document.createElement('div');
  bubble.className = 'message-content';

  if (role === 'bot') {
    // Render markdown HTML
    bubble.innerHTML = content;

    // Add sources if available
    if (sources && sources.length > 0) {
      const sourcesDiv = document.createElement('div');
      sourcesDiv.className = 'sources';

      const label = document.createElement('div');
      label.className = 'sources-label';
      label.innerHTML = `
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1-2.5-2.5Z"></path>
          <path d="M6 6h10"></path>
          <path d="M6 10h10"></path>
        </svg>
        <span>Sources</span>
      `;
      sourcesDiv.appendChild(label);

      const listDiv = document.createElement('div');
      listDiv.className = 'sources-list';

      sources.forEach((src) => {
        const tag = document.createElement('span');
        tag.className = 'source-tag';
        tag.innerHTML = `<span class="source-icon">📄</span><span>${escapeHtml(src)}</span>`;
        listDiv.appendChild(tag);
      });

      sourcesDiv.appendChild(listDiv);
      bubble.appendChild(sourcesDiv);
    }

    bubbleWrapper.appendChild(bubble);

    // Bot Action Toolbar (Copy Button)
    const actionsToolbar = document.createElement('div');
    actionsToolbar.className = 'message-actions';

    const copyBtn = document.createElement('button');
    copyBtn.className = 'action-btn';
    copyBtn.title = 'Copy response';
    copyBtn.innerHTML = `
      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <rect width="14" height="14" x="8" y="8" rx="2" ry="2"></rect>
        <path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"></path>
      </svg>
      <span>Copy</span>
    `;

    copyBtn.addEventListener('click', async () => {
      try {
        const textToCopy = bubble.innerText;
        await navigator.clipboard.writeText(textToCopy);
        copyBtn.classList.add('copied');
        copyBtn.innerHTML = `
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="20 6 9 17 4 12"></polyline>
          </svg>
          <span>Copied!</span>
        `;
        setTimeout(() => {
          copyBtn.classList.remove('copied');
          copyBtn.innerHTML = `
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <rect width="14" height="14" x="8" y="8" rx="2" ry="2"></rect>
              <path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"></path>
            </svg>
            <span>Copy</span>
          `;
        }, 2000);
      } catch (err) {
        console.error('Failed to copy text:', err);
      }
    });

    actionsToolbar.appendChild(copyBtn);
    bubbleWrapper.appendChild(actionsToolbar);

  } else {
    bubble.textContent = content;
    bubbleWrapper.appendChild(bubble);
  }

  msg.appendChild(avatar);
  msg.appendChild(bubbleWrapper);
  chatArea.appendChild(msg);
  scrollToBottom();
}

function appendError(message) {
  const el = document.createElement('div');
  el.className = 'error-message';
  el.innerHTML = `
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <circle cx="12" cy="12" r="10"></circle>
      <line x1="12" x2="12" y1="8" y2="12"></line>
      <line x1="12" x2="12.01" y1="16" y2="16"></line>
    </svg>
    <span>${escapeHtml(message)}</span>
  `;
  chatArea.appendChild(el);
  scrollToBottom();
}

function showTypingIndicator() {
  const indicator = document.createElement('div');
  indicator.className = 'typing-indicator';
  indicator.innerHTML = `
    <div class="message-avatar">
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M12 8V4H8"></path>
        <rect width="16" height="12" x="4" y="8" rx="2"></rect>
        <path d="M2 14h2"></path>
        <path d="M20 14h2"></path>
        <path d="M15 13v2"></path>
        <path d="M9 13v2"></path>
      </svg>
    </div>
    <div class="typing-dots">
      <span></span>
      <span></span>
      <span></span>
    </div>
  `;
  chatArea.appendChild(indicator);
  scrollToBottom();
  return indicator;
}

function setLoading(loading) {
  isLoading = loading;
  sendBtn.disabled = loading;
  questionInput.disabled = loading;
  if (!loading) {
    questionInput.focus();
  }
}

function scrollToBottom() {
  requestAnimationFrame(() => {
    chatArea.scrollTop = chatArea.scrollHeight;
  });
}

function escapeHtml(str) {
  if (!str) return '';
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}
