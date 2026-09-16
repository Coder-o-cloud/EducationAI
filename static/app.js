/**
 * EduGPT - Production-Ready Frontend Client Logic
 * Features: Multi-agent debate visualization, Syllabus parsing & progress tracking,
 * IME-safe Chat, Markdown rendering, and Settings management.
 */

// Application State
const state = {
  currentTopic: '',
  currentSyllabus: '',
  activeTab: 'studio',
  isGenerating: false,
  isChatting: false,
  modules: [],
  completedModules: new Set(),
};

// DOM Elements
const elements = {
  // Tabs
  tabStudio: document.getElementById('tab-studio'),
  tabClassroom: document.getElementById('tab-classroom'),
  viewStudio: document.getElementById('studio-view'),
  viewClassroom: document.getElementById('classroom-view'),
  activeCoursePill: document.getElementById('active-course-pill'),

  // Status & Settings
  statusLabel: document.getElementById('status-label'),
  systemStatusIndicator: document.getElementById('system-status-indicator'),
  btnOpenSettings: document.getElementById('btn-open-settings'),
  settingsModal: document.getElementById('settings-modal'),
  btnCloseModal: document.getElementById('btn-close-modal'),
  btnCancelSettings: document.getElementById('btn-cancel-settings'),
  btnSaveSettings: document.getElementById('btn-save-settings'),
  settingsApiKey: document.getElementById('settings-api-key'),
  settingsStatusText: document.getElementById('settings-status-text'),

  // Studio
  topicForm: document.getElementById('topic-form'),
  topicInput: document.getElementById('topic-input'),
  btnBuildSyllabus: document.getElementById('btn-build-syllabus'),
  topicPills: document.querySelectorAll('.topic-pill'),
  agentVisualizer: document.getElementById('agent-visualizer'),
  stage1: document.getElementById('stage-1'),
  stage2: document.getElementById('stage-2'),
  stage3: document.getElementById('stage-3'),
  syllabusResultSection: document.getElementById('syllabus-result-section'),
  syllabusTopicTitle: document.getElementById('syllabus-topic-title'),
  syllabusContent: document.getElementById('syllabus-content'),
  btnCopySyllabus: document.getElementById('btn-copy-syllabus'),
  btnDownloadSyllabus: document.getElementById('btn-download-syllabus'),
  btnStartLearning: document.getElementById('btn-start-learning'),

  // Classroom
  sidebarCourseTitle: document.getElementById('sidebar-course-title'),
  sidebarModulesList: document.getElementById('sidebar-modules-list'),
  courseProgressFill: document.getElementById('course-progress-fill'),
  modulesCompletedLabel: document.getElementById('modules-completed-label'),
  progressPercent: document.getElementById('progress-percent'),
  btnGoToStudio: document.getElementById('btn-go-to-studio'),
  btnResetChat: document.getElementById('btn-reset-chat'),
  btnClearChat: document.getElementById('btn-clear-chat'),
  chatMessagesContainer: document.getElementById('chat-messages-container'),
  chatForm: document.getElementById('chat-form'),
  chatInput: document.getElementById('chat-input'),
  btnSendMessage: document.getElementById('btn-send-message'),
  promptChips: document.querySelectorAll('.prompt-chip'),
  toastContainer: document.getElementById('toast-container'),
};

// ==========================================================================
// Initialization
// ==========================================================================
document.addEventListener('DOMContentLoaded', () => {
  initTabs();
  initTopicSubmission();
  initChat();
  initSettings();
  initQuickPills();
  initExportButtons();
  loadSavedState();
  checkSystemStatus();
});

// ==========================================================================
// Tab Switching
// ==========================================================================
function initTabs() {
  const switchTab = (target) => {
    state.activeTab = target === 'classroom-view' ? 'classroom' : 'studio';

    elements.tabStudio.classList.toggle('active', state.activeTab === 'studio');
    elements.tabStudio.setAttribute('aria-selected', state.activeTab === 'studio');
    elements.viewStudio.classList.toggle('active', state.activeTab === 'studio');

    elements.tabClassroom.classList.toggle('active', state.activeTab === 'classroom');
    elements.tabClassroom.setAttribute('aria-selected', state.activeTab === 'classroom');
    elements.viewClassroom.classList.toggle('active', state.activeTab === 'classroom');

    if (state.activeTab === 'classroom') {
      elements.chatInput?.focus();
      scrollChatToBottom();
    }
  };

  elements.tabStudio.addEventListener('click', () => switchTab('studio-view'));
  elements.tabClassroom.addEventListener('click', () => switchTab('classroom-view'));

  if (elements.btnStartLearning) {
    elements.btnStartLearning.addEventListener('click', () => {
      switchTab('classroom-view');
    });
  }

  if (elements.btnGoToStudio) {
    elements.btnGoToStudio.addEventListener('click', () => {
      switchTab('studio-view');
    });
  }
}

// ==========================================================================
// Topic Submission & Syllabus Generation
// ==========================================================================
function initTopicSubmission() {
  elements.topicForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const topic = elements.topicInput.value.trim();
    if (!topic || state.isGenerating) return;

    await generateCourseSyllabus(topic);
  });
}

function initQuickPills() {
  elements.topicPills.forEach((pill) => {
    pill.addEventListener('click', () => {
      const topic = pill.dataset.topic;
      if (topic) {
        elements.topicInput.value = topic;
        generateCourseSyllabus(topic);
      }
    });
  });
}

async function generateCourseSyllabus(topic) {
  state.isGenerating = true;
  elements.btnBuildSyllabus.disabled = true;
  elements.btnBuildSyllabus.querySelector('.btn-text').textContent = 'Agents Debating...';

  // Show visualizer and reset stages
  elements.agentVisualizer.style.display = 'block';
  elements.syllabusResultSection.style.display = 'none';

  setStageState(elements.stage1, 'active', 'Analyzing domain...');
  setStageState(elements.stage2, 'running', '<span class="spin"></span> Debating syllabus...');
  setStageState(elements.stage3, 'pending', 'Pending');

  // Simulated visual stage transitions while request is processing
  const stageTimeout = setTimeout(() => {
    setStageState(elements.stage1, 'active', 'Complete');
    setStageState(elements.stage2, 'active', 'Dialogue finished');
    setStageState(elements.stage3, 'running', '<span class="spin"></span> Structuring syllabus...');
  }, 4500);

  try {
    const response = await fetch('/api/generate-syllabus', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ topic }),
    });

    clearTimeout(stageTimeout);

    if (!response.ok) {
      let errMsg = 'Failed to generate syllabus';
      try {
        const errData = await response.json();
        errMsg = errData.detail || errData.message || errMsg;
      } catch (e) {
        errMsg = await response.text();
      }
      throw new Error(errMsg);
    }

    const data = await response.json();


    // Mark all stages complete
    setStageState(elements.stage1, 'active', 'Complete');
    setStageState(elements.stage2, 'active', 'Complete');
    setStageState(elements.stage3, 'active', 'Synthesized');

    setTimeout(() => {
      elements.agentVisualizer.style.display = 'none';
      renderSyllabus(data.topic, data.syllabus);
      if (data.notice) {
        showToast(data.notice, 'info');
      } else {
        showToast('Syllabus created successfully by AI Agents!', 'success');
      }
    }, 600);

  } catch (error) {
    clearTimeout(stageTimeout);
    elements.agentVisualizer.style.display = 'none';
    showToast(`Error: ${error.message}`, 'error');
  } finally {
    state.isGenerating = false;
    elements.btnBuildSyllabus.disabled = false;
    elements.btnBuildSyllabus.querySelector('.btn-text').textContent = 'Generate Syllabus';
  }
}

function setStageState(stageEl, stateClass, statusHtml) {
  stageEl.className = `stage-item ${stateClass}`;
  const statusEl = stageEl.querySelector('.stage-status');
  if (statusEl) statusEl.innerHTML = statusHtml;
}

function renderSyllabus(topic, syllabusMarkdown) {
  state.currentTopic = topic;
  state.currentSyllabus = syllabusMarkdown;
  state.completedModules.clear();

  elements.syllabusTopicTitle.textContent = topic;
  elements.syllabusContent.innerHTML = formatMarkdown(syllabusMarkdown);
  elements.syllabusResultSection.style.display = 'block';

  // Update Classroom Sidebar
  elements.sidebarCourseTitle.textContent = topic;
  elements.activeCoursePill.style.display = 'inline-block';

  // Parse modules for the sidebar checklist
  parseSyllabusModules(syllabusMarkdown);

  // Save to localStorage
  try {
    localStorage.setItem('edugpt_topic', topic);
    localStorage.setItem('edugpt_syllabus', syllabusMarkdown);
  } catch (e) {
    console.warn('LocalStorage save failed', e);
  }
}

// ==========================================================================
// Syllabus Parsing & Roadmap Checklist
// ==========================================================================
function parseSyllabusModules(markdown) {
  const lines = markdown.split('\n');
  const modules = [];

  const moduleRegex = /(?:module|chapter|week|section|unit|part)\s*\d+[\s\:\-\–]+([^\n\r#]+)/i;
  const headerRegex = /^#{2,3}\s+(.+)$/;

  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed) continue;

    const modMatch = trimmed.match(moduleRegex);
    const headMatch = trimmed.match(headerRegex);

    if (modMatch) {
      modules.push({ title: trimmed.replace(/^#+\s*/, '') });
    } else if (headMatch && modules.length < 10) {
      // Fallback: headers as modules if no explicit "Module X"
      if (!headMatch[1].toLowerCase().includes('prerequisite') && !headMatch[1].toLowerCase().includes('syllabus')) {
        modules.push({ title: headMatch[1] });
      }
    }
  }

  // Deduplicate and fallback if empty
  state.modules = modules.length > 0 ? modules : [
    { title: 'Module 1: Foundations & Core Concepts' },
    { title: 'Module 2: Practical Implementation' },
    { title: 'Module 3: Advanced Topics & Case Studies' },
  ];

  renderSidebarModules();
}

function renderSidebarModules() {
  elements.sidebarModulesList.innerHTML = '';

  state.modules.forEach((mod, index) => {
    const item = document.createElement('div');
    item.className = 'module-nav-item';
    if (index === 0) item.classList.add('active');

    const isChecked = state.completedModules.has(index);

    item.innerHTML = `
      <input type="checkbox" class="module-checkbox" id="mod-check-${index}" ${isChecked ? 'checked' : ''}>
      <div class="module-info">
        <span class="module-name">${escapeHtml(mod.title)}</span>
        <span class="module-subtitle">Click to jump into discussion</span>
      </div>
    `;

    // Handle check completion
    const checkbox = item.querySelector('.module-checkbox');
    checkbox.addEventListener('click', (e) => {
      e.stopPropagation();
      if (checkbox.checked) {
        state.completedModules.add(index);
      } else {
        state.completedModules.delete(index);
      }
      updateProgress();
    });

    // Clicking module prompts instructor in chat
    item.addEventListener('click', () => {
      document.querySelectorAll('.module-nav-item').forEach(el => el.classList.remove('active'));
      item.classList.add('active');
      sendChatMessage(`Let's focus on: "${mod.title}". Can you explain the concepts in this section?`);
    });

    elements.sidebarModulesList.appendChild(item);
  });

  updateProgress();
}

function updateProgress() {
  const total = state.modules.length || 1;
  const completed = state.completedModules.size;
  const percent = Math.round((completed / total) * 100);

  elements.courseProgressFill.style.width = `${percent}%`;
  elements.progressPercent.textContent = `${percent}%`;
  elements.modulesCompletedLabel.textContent = `${completed} of ${total} Completed`;
}

// ==========================================================================
// Interactive Classroom Chat (IME-Safe)
// ==========================================================================
function initChat() {
  // IME-safe Enter to submit handling
  elements.chatInput.addEventListener('keydown', (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();

      // Block submission if user is composing via IME (e.g. Japanese, Chinese)
      if (event.isComposing || event.keyCode === 229) {
        return;
      }

      elements.chatForm.requestSubmit();
    }
  });

  // Auto-grow textarea
  elements.chatInput.addEventListener('input', () => {
    elements.chatInput.style.height = 'auto';
    elements.chatInput.style.height = Math.min(elements.chatInput.scrollHeight, 140) + 'px';
  });

  // Chat Form Submission
  elements.chatForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const message = elements.chatInput.value.trim();
    if (!message || state.isChatting) return;

    elements.chatInput.value = '';
    elements.chatInput.style.height = 'auto';
    sendChatMessage(message);
  });

  // Quick Prompt Chips
  elements.promptChips.forEach((chip) => {
    chip.addEventListener('click', () => {
      const prompt = chip.dataset.prompt;
      if (prompt && !state.isChatting) {
        sendChatMessage(prompt);
      }
    });
  });

  // Clear Chat
  elements.btnClearChat.addEventListener('click', () => {
    elements.chatMessagesContainer.innerHTML = `
      <div class="message-bubble system-welcome">
        <div class="bubble-avatar">🤖</div>
        <div class="bubble-content markdown-body">
          <p><strong>Chat Cleared.</strong></p>
          <p>Feel free to ask your instructor a new question or continue with the next module.</p>
        </div>
      </div>
    `;
  });

  // Reset Chat Conversation Session
  elements.btnResetChat.addEventListener('click', async () => {
    try {
      await fetch('/api/reset', { method: 'POST' });
      elements.btnClearChat.click();
      showToast('Instructor session reset successfully.', 'success');
    } catch (e) {
      showToast('Failed to reset session.', 'error');
    }
  });
}

async function sendChatMessage(message) {
  if (!state.currentSyllabus) {
    showToast('Please generate a course syllabus in Course Studio first!', 'error');
    return;
  }

  state.isChatting = true;
  elements.btnSendMessage.disabled = true;

  // Append user message bubble
  appendMessageBubble('user', message);
  scrollChatToBottom();

  // Show typing indicator
  const typingEl = showTypingIndicator();
  scrollChatToBottom();

  try {
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message }),
    });

    typingEl.remove();

    if (!response.ok) {
      let errMsg = 'Instructor response failed';
      try {
        const errData = await response.json();
        errMsg = errData.detail || errData.message || errMsg;
      } catch (e) {
        errMsg = await response.text();
      }
      throw new Error(errMsg);
    }

    const data = await response.json();
    appendMessageBubble('instructor', data.reply);
    scrollChatToBottom();


  } catch (error) {
    typingEl.remove();
    appendMessageBubble('instructor', `⚠️ *An error occurred:* ${error.message}`);
    showToast(error.message, 'error');
    scrollChatToBottom();
  } finally {
    state.isChatting = false;
    elements.btnSendMessage.disabled = false;
    elements.chatInput.focus();
  }
}

function appendMessageBubble(sender, text) {
  const bubble = document.createElement('div');
  bubble.className = `message-bubble ${sender}-message`;

  const avatar = sender === 'user' ? '👤' : '🎓';
  const renderedContent = sender === 'user' ? escapeHtml(text).replace(/\n/g, '<br>') : formatMarkdown(text);

  bubble.innerHTML = `
    <div class="bubble-avatar">${avatar}</div>
    <div class="bubble-content markdown-body">${renderedContent}</div>
  `;

  elements.chatMessagesContainer.appendChild(bubble);
  return bubble;
}

function showTypingIndicator() {
  const typingBubble = document.createElement('div');
  typingBubble.className = 'message-bubble instructor-message';
  typingBubble.innerHTML = `
    <div class="bubble-avatar">🎓</div>
    <div class="typing-bubble">
      <div class="dot"></div>
      <div class="dot"></div>
      <div class="dot"></div>
    </div>
  `;
  elements.chatMessagesContainer.appendChild(typingBubble);
  return typingBubble;
}

function scrollChatToBottom() {
  elements.chatMessagesContainer.scrollTop = elements.chatMessagesContainer.scrollHeight;
}

// ==========================================================================
// Settings Modal & API Status
// ==========================================================================
function initSettings() {
  const settingsApiBase = document.getElementById('settings-api-base');
  const btnActivateDemo = document.getElementById('btn-activate-demo');

  const openModal = () => {
    elements.settingsModal.style.display = 'flex';
    checkSystemStatus();
  };

  const closeModal = () => {
    elements.settingsModal.style.display = 'none';
  };

  elements.btnOpenSettings.addEventListener('click', openModal);
  elements.btnCloseModal.addEventListener('click', closeModal);
  elements.btnCancelSettings.addEventListener('click', closeModal);

  // Close on backdrop click
  elements.settingsModal.addEventListener('click', (e) => {
    if (e.target === elements.settingsModal) closeModal();
  });

  // Activate Demo Mode
  if (btnActivateDemo) {
    btnActivateDemo.addEventListener('click', async () => {
      try {
        await fetch('/api/settings', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ demo_mode: true }),
        });
        showToast('Demo Mode activated! You can now generate syllabi without an API key.', 'success');
        closeModal();
        checkSystemStatus();
      } catch (e) {
        showToast('Failed to toggle demo mode', 'error');
      }
    });
  }

  // Save Settings
  elements.btnSaveSettings.addEventListener('click', async () => {
    const key = elements.settingsApiKey.value.trim();
    const model = settingsApiBase ? settingsApiBase.value.trim() : '';

    const payload = {};
    if (key) payload.api_key = key;
    if (model) payload.model_name = model;

    try {
      const res = await fetch('/api/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      if (res.ok) {
        showToast('Settings saved successfully!', 'success');
        closeModal();
        checkSystemStatus();
      }
    } catch (e) {
      showToast('Failed to save settings', 'error');
    }
  });
}

async function checkSystemStatus() {
  try {
    const res = await fetch('/api/status');
    if (res.ok) {
      const data = await res.json();
      const settingsApiBase = document.getElementById('settings-api-base');
      if (settingsApiBase && data.model_name) {
        settingsApiBase.value = data.model_name;
      }

      if (data.demo_mode) {
        elements.statusLabel.textContent = 'Demo Mode';
        elements.systemStatusIndicator.style.borderColor = 'rgba(99, 102, 241, 0.4)';
        elements.settingsStatusText.textContent = 'Demo Mode Active (Offline / Simulation)';
      } else if (data.api_key_configured) {
        elements.statusLabel.textContent = 'Gemini Online';
        elements.systemStatusIndicator.style.borderColor = 'rgba(16, 185, 129, 0.25)';
        elements.settingsStatusText.textContent = `Gemini (${data.model_name || 'gemini-3.8-flash'}): ${data.api_key_masked}`;
      } else {
        elements.statusLabel.textContent = 'API Key Needed';
        elements.systemStatusIndicator.style.borderColor = 'rgba(245, 158, 11, 0.4)';
        elements.settingsStatusText.textContent = 'No Gemini API key configured in .env';
      }
    }

  } catch (e) {
    elements.statusLabel.textContent = 'Offline';
    elements.systemStatusIndicator.style.borderColor = 'rgba(244, 63, 94, 0.4)';
  }
}

// ==========================================================================
// Copy & Export Helpers
// ==========================================================================
function initExportButtons() {
  elements.btnCopySyllabus.addEventListener('click', () => {
    if (!state.currentSyllabus) return;
    navigator.clipboard.writeText(state.currentSyllabus).then(() => {
      showToast('Syllabus copied to clipboard!', 'success');
    });
  });

  elements.btnDownloadSyllabus.addEventListener('click', () => {
    if (!state.currentSyllabus) return;
    const blob = new Blob([state.currentSyllabus], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${(state.currentTopic || 'syllabus').toLowerCase().replace(/\s+/g, '_')}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    showToast('Downloaded syllabus markdown file!', 'success');
  });
}

// ==========================================================================
// LocalStorage Persistence
// ==========================================================================
function loadSavedState() {
  try {
    const savedTopic = localStorage.getItem('edugpt_topic');
    const savedSyllabus = localStorage.getItem('edugpt_syllabus');
    if (savedTopic && savedSyllabus) {
      renderSyllabus(savedTopic, savedSyllabus);
    }
  } catch (e) {
    console.warn('LocalStorage retrieval failed', e);
  }
}

// ==========================================================================
// Lightweight Markdown Formatter
// ==========================================================================
function formatMarkdown(text) {
  if (!text) return '';

  let html = text;

  // Code blocks with syntax copy button
  html = html.replace(/```([a-zA-Z0-9_-]*)\n([\s\S]*?)```/g, (match, lang, code) => {
    return `<pre><code class="language-${lang || 'text'}">${escapeHtml(code.trim())}</code></pre>`;
  });

  // Inline code
  html = html.replace(/`([^`]+)`/g, '<code>$1</code>');

  // Headers
  html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>');
  html = html.replace(/^## (.*$)/gim, '<h2>$1</h2>');
  html = html.replace(/^# (.*$)/gim, '<h1>$1</h1>');

  // Bold and Italics
  html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
  html = html.replace(/\*([^*]+)\*/g, '<em>$1</em>');

  // Blockquotes
  html = html.replace(/^\> (.*$)/gim, '<blockquote>$1</blockquote>');

  // Unordered Lists
  html = html.replace(/^\s*[-*]\s+(.*$)/gim, '<li>$1</li>');
  html = html.replace(/(<li>.*<\/li>)/gims, '<ul>$1</ul>');

  // Ordered Lists
  html = html.replace(/^\s*(\d+)\.\s+(.*$)/gim, '<li>$2</li>');

  // Paragraphs for double line breaks
  html = html.replace(/\n\n+/g, '</p><p>');

  // Wrap in paragraph if not starting with block element
  if (!html.startsWith('<h') && !html.startsWith('<ul') && !html.startsWith('<pre') && !html.startsWith('<blockquote')) {
    html = `<p>${html}</p>`;
  }

  return html;
}

function escapeHtml(str) {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

// Toast Notifications
function showToast(message, type = 'info') {
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.innerHTML = `
    <span>${type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️'}</span>
    <span>${escapeHtml(message)}</span>
  `;

  elements.toastContainer.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
    toast.style.transition = 'all 0.25s ease';
    setTimeout(() => toast.remove(), 250);
  }, 4000);
}
