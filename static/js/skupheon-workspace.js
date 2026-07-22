/* =============================================
   SKUPHEON AI — Complete Workspace Redesign JS
   ============================================= */

(function () {
  'use strict';

  const $ = (sel, ctx) => (ctx || document).querySelector(sel);
  const $$ = (sel, ctx) => [...(ctx || document).querySelectorAll(sel)];

  const DOM = {
    sidebar: $('#saw-sidebar'),
    sidebarList: $('#saw-sidebar-list'),
    sidebarSearch: $('#saw-sidebar-search'),
    newChatBtn: $('#saw-new-chat'),
    clearAllBtn: $('#saw-clear-all'),
    messages: $('#saw-messages'),
    messagesInner: $('#saw-messages-inner'),
    msgContainer: $('#saw-msg-container'),
    welcome: $('#saw-welcome'),
    typing: $('#saw-typing'),
    input: $('#saw-input'),
    sendBtn: $('#saw-send-btn'),
    attachBtn: $('#saw-attach-btn'),
    voiceBtn: $('#saw-voice-btn'),
    fileInput: $('#saw-file-input'),
    attachments: $('#saw-attachments'),
    composerBox: $('#saw-composer-box'),
    dropOverlay: $('#saw-drop-overlay'),
    contextMenu: $('#saw-context-menu'),
    itemMenu: $('#saw-item-menu'),
    toast: $('#saw-toast'),
    toastText: $('#saw-toast-text'),
    suggestions: $('#saw-suggestions'),
    modalOverlay: $('#saw-modal-overlay'),
    modalTitle: $('#saw-modal-title'),
    modalBody: $('#saw-modal-body'),
    modalInputWrap: $('#saw-modal-input-wrap'),
    modalInput: $('#saw-modal-input'),
    modalCancel: $('#saw-modal-cancel'),
    modalConfirm: $('#saw-modal-confirm'),
    modalClose: $('#saw-modal-close'),
    editActions: $('#saw-edit-actions'),
    editCancel: $('#saw-edit-cancel'),
    editResend: $('#saw-edit-resend'),
    readAloudBtn: $('#saw-read-aloud-btn'),
    mytripBtn: $('#saw-mytrip-btn'),
    mytripStatus: $('#saw-mytrip-status'),
    scopeBar: $('#saw-scope-bar'),
    scopeTrips: $('#saw-scope-trips'),
    scopeDestinations: $('#saw-scope-destinations'),
  };

  let state = {
    sessionId: null,
    isTyping: false,
    sessions: [],
    contextTarget: null,
    pendingFiles: [],
    recognition: null,
    isRecording: false,
    itemMenuTarget: null,
    isSpeaking: false,
    speakingMsgEl: null,
    myTripConnected: false,
    myTripScope: null, // 'trips' | 'destinations' | null
  };

  /* ── Daily Content Pool ──────────────────────── */
  const SUGGESTION_POOL = [
    { icon: 'route', title: 'Plan a Trip', desc: 'Full itinerary with hotels, transport & budget', prompt: 'Plan a 5-day trip to Himachal Pradesh with a budget of 25000 INR' },
    { icon: 'calendar_month', title: 'Best Time to Visit', desc: 'Seasonal recommendations for any destination', prompt: 'Suggest the best time to visit Rajasthan and why' },
    { icon: 'account_balance_wallet', title: 'Budget Planner', desc: 'Detailed cost breakdown for any trip', prompt: 'Create a budget breakdown for a solo trip to North Goa for 4 days' },
    { icon: 'compare_arrows', title: 'Compare Destinations', desc: 'Side-by-side comparison with recommendations', prompt: 'Compare Manali vs Shimla for a honeymoon trip' },
    { icon: 'directions_car', title: 'Road Trip Planner', desc: 'Route, stops, fuel costs & stay options', prompt: 'Suggest a 7-day South India road trip itinerary starting from Bangalore' },
    { icon: 'family_restroom', title: 'Family Vacation', desc: 'Kid-friendly resorts, activities & safety tips', prompt: 'What are the best family-friendly resorts in Kerala with activities for kids?' },
    { icon: 'work', title: 'Business Trip Planner', desc: 'Hotels, meetings & city tips', prompt: 'Plan a 3-day business trip to Mumbai with hotel near BKC and evening leisure options' },
    { icon: 'savings', title: 'Budget Travel', desc: 'Travel more, spend less', prompt: 'Create a detailed budget for a 7-day solo trip to North Goa under 15000' },
    { icon: 'map', title: 'Road Trip', desc: 'Self-drive routes with stops & fuel', prompt: 'Plan a road trip from Bangalore to Coorg with route, stops, fuel cost and stay options' },
    { icon: 'luggage', title: 'Packing Guide', desc: 'Smart packing for any destination', prompt: 'Create a packing list for a 5-day trip to Ladakh in September including layering tips' },
    { icon: 'wb_sunny', title: 'Summer Escapes', desc: 'Beat the heat with these cool spots', prompt: 'Suggest the coolest hill stations in India to visit in May with budget breakdown' },
    { icon: 'card_travel', title: 'Solo Travel', desc: 'Safe & exciting solo destinations', prompt: 'Plan a safe solo trip to Spiti Valley with itinerary, stays and safety tips' },
    { icon: 'flight', title: 'Flight Planning', desc: 'Best routes, timing & airline tips', prompt: 'Find the best time to book flights for a Delhi to Goa trip and suggest airlines' },
    { icon: 'temple_buddhist', title: 'Pilgrimage Trips', desc: 'Sacred journeys across the world', prompt: 'Plan a Char Dham Yatra itinerary with routes, stays and essential tips' },
    { icon: 'celebration', title: 'Honeymoon Planner', desc: 'Romantic destinations & experiences', prompt: 'Plan a 6-day honeymoon trip to Andaman with romantic activities and budget' },
    { icon: 'local_florist', title: 'Garden City Trips', desc: 'Botanical gardens & nature walks', prompt: 'Plan a peaceful trip to Munnar and Thekkady with garden and plantation visits' },
    { icon: 'downhill_skiing', title: 'Winter Sports', desc: 'Skiing, snow & adventure', prompt: 'Suggest winter adventure activities in Auli with skiing details and stay options' },
    { icon: 'wallet', title: 'Trip Budgeter', desc: 'AI-powered cost estimation', prompt: 'Create a detailed day-by-day budget for a 5-day trip to Manali for 2 people' },
    { icon: 'hotel', title: 'Hotel Finder', desc: 'Best stays at every price point', prompt: 'Suggest the best boutique hotels in Jaipur under 3000 per night with reviews' },
    { icon: 'train', title: 'Train Routes', desc: 'Scenic rail journeys around the world', prompt: 'Suggest the most scenic train routes in Switzerland with class options and booking tips' },
    { icon: 'local_bar', title: 'Weekend Drinks', desc: 'Winery & brewery tours', prompt: 'Plan a weekend winery tour near Mumbai with tastings and stays' },
    { icon: 'surfing', title: 'Coastal Explorer', desc: 'Beaches, cliffs & coastal drives', prompt: 'Plan a coastal road trip from Goa to Gokarna with beach stops and stays' },
    { icon: 'backpack', title: 'Backpacking Guide', desc: 'Light travel, big adventures', prompt: 'Plan a 10-day backpacking trip across Himachal Pradesh on a tight budget' },
    { icon: 'local_cafe', title: 'Cafe Hopping', desc: 'Best cafe culture destinations', prompt: 'Create a cafe hopping itinerary for Pondicherry with top cafes and beaches' },
    { icon: 'park', title: 'Wildlife Safari', desc: 'Jungle safaris & animal encounters', prompt: 'Plan a wildlife safari trip to Ranthambore with booking tips and best zones' },
    { icon: 'temple_hindu', title: 'Heritage Trail', desc: 'Historic forts, palaces & temples', prompt: 'Suggest a 5-day heritage trail across Rajasthan with must-visit monuments' },
    { icon: 'restaurant', title: 'Food Trail', desc: 'Best street food routes around the world', prompt: 'Create a food trail itinerary for Delhi covering the best street food spots' },
    { icon: 'beach_access', title: 'Beach Escape', desc: 'Pristine beaches & coastal towns', prompt: 'Suggest the best quiet beaches in Goa for a relaxing 4-day trip' },
    { icon: 'hiking', title: 'Trek Adventure', desc: 'Top trekking routes for all levels', prompt: 'Recommend easy to moderate treks near Manali with trail details and stay options' },
    { icon: 'flight_takeoff', title: 'International Trips', desc: 'Visa, flights & destination guides', prompt: 'Suggest budget-friendly international trips from India with visa requirements' },
    { icon: 'local_florist', title: 'Wellness Retreat', desc: 'Yoga, meditation & spa', prompt: 'Plan a 5-day wellness retreat in Rishikesh with yoga and Ayurveda treatments' },
    { icon: 'castle', title: 'Fort Trail', desc: 'Royal heritage across the world', prompt: 'Create a Rajasthan fort trail covering Mehrangarh, Amber, Kumbhalgarh and Chittorgarh' },
    { icon: 'kayaking', title: 'River Adventures', desc: 'Rafting, kayaking & more', prompt: 'Plan a river adventure trip to Rishikesh with rafting, cliff jumping and camping' },
    { icon: 'sports_motorsports', title: 'Epic Drive', desc: 'Self-drive circuits & routes', prompt: 'Plan an epic self-drive circuit from Delhi through Rajasthan covering 5 cities' },
    { icon: 'scuba_diving', title: 'Scuba Trips', desc: 'Underwater adventures around the world', prompt: 'Best scuba diving spots in India with certification options and costs' },
  ];

  const CHIP_POOL = [
    { icon: 'diamond', label: 'Hidden Gems', prompt: 'What are the best hidden gems in Rajasthan?' },
    { icon: 'checklist', label: 'Packing List', prompt: 'What should I pack for a hill station in December?' },
    { icon: 'favorite', label: 'Romantic Trip', prompt: 'Plan a romantic getaway to Udaipur for 3 days' },
    { icon: 'explore', label: 'Offbeat Places', prompt: 'Suggest offbeat destinations in South India' },
    { icon: 'paragliding', label: 'Adventure Sports', prompt: 'What are the best adventure activities in Rishikesh?' },
    { icon: 'tour', label: 'Golden Triangle', prompt: 'Create a 10-day India Golden Triangle itinerary with Delhi, Agra and Jaipur' },
    { icon: 'beach_access', label: 'Quiet Beaches', prompt: 'Suggest best beaches in India for a quiet and peaceful vacation' },
    { icon: 'weekend', label: 'Weekend Getaway', prompt: 'Plan a weekend trip to Manali from Delhi with budget options' },
    { icon: 'flight', label: 'Flight Deals', prompt: 'Suggest the cheapest flight routes in India for next month' },
    { icon: 'train', label: 'Train Journeys', prompt: 'Best scenic train routes in India with booking tips' },
    { icon: 'camping', label: 'Camping Spots', prompt: 'Suggest the best camping sites near Bangalore with activities' },
    { icon: 'mountain', label: 'Hill Stations', prompt: 'Compare the top 5 hill stations in North India for couples' },
    { icon: 'photo_camera', label: 'Photography', prompt: 'Suggest photogenic destinations in India for landscape photography' },
    { icon: 'spa', label: 'Wellness Retreats', prompt: 'Best Ayurveda and wellness retreats in Kerala' },
    { icon: 'directions_bike', label: 'Cycling Routes', prompt: 'Suggest scenic cycling routes in South India for beginners' },
    { icon: 'backpack', label: 'Backpacking', prompt: 'Plan a 10-day backpacking trip across Himachal Pradesh on a tight budget' },
    { icon: 'eco', label: 'Eco Tourism', prompt: 'Suggest eco-friendly destinations and sustainable travel tips in India' },
    { icon: 'nightlife', label: 'Nightlife', prompt: 'Best nightlife cities in India with top bars and clubs' },
    { icon: 'shopping_bag', label: 'Shopping', prompt: 'Best shopping markets in Jaipur, Delhi and Mumbai with what to buy' },
    { icon: 'water', label: 'Water Sports', prompt: 'Best water sports destinations in India with activities and costs' },
    { icon: 'music_note', label: 'Festivals', prompt: 'Upcoming music and cultural festivals in India with travel plans' },
    { icon: 'local_cafe', label: 'Cafe Hopping', prompt: 'Best cafe culture cities in India with top cafe recommendations' },
    { icon: 'park', label: 'National Parks', prompt: 'Best national parks in India for wildlife safari with booking tips' },
    { icon: 'architecture', label: 'Architecture', prompt: 'Must-see architectural marvels across India with history' },
    { icon: 'sports_motorsports', label: 'Rally Routes', prompt: 'Epic self-drive rally routes across Rajasthan' },
    { icon: 'grass', label: 'Tea Gardens', prompt: 'Plan a tea garden tour in Darjeeling and Munnar' },
    { icon: 'downhill_skiing', label: 'Skiing', prompt: 'Best skiing destinations in India for beginners' },
    { icon: 'local_bar', label: 'Brewery Tours', prompt: 'Best craft beer breweries to visit across India' },
  ];

  const GUIDE_POOL = [
    { icon: 'terrain', title: 'Kashmir Guide', prompt: 'Give me a complete guide for visiting Kashmir including places, food, transport and budget' },
    { icon: 'restaurant', title: 'Jaipur Food', prompt: 'What are the must-try street foods in Jaipur and where to find them?' },
    { icon: 'umbrella', title: 'Monsoon Trips', prompt: 'List the best monsoon destinations in India with travel tips' },
    { icon: 'compare', title: 'Travel Modes', prompt: 'Compare flight vs train vs bus for Delhi to Manali with cost and time' },
    { icon: 'terrain', title: 'Ladakh Guide', prompt: 'Complete Ladakh travel guide with routes, permits, altitude tips and budget' },
    { icon: 'restaurant', title: 'Kerala Cuisine', prompt: 'Must-try Kerala dishes and where to find authentic food in Kochi and Trivandrum' },
    { icon: 'umbrella', title: 'Monsoon Ready', prompt: 'How to travel during monsoon season in India — tips, gear, and best destinations' },
    { icon: 'compare', title: 'Manali vs Shimla', prompt: 'Detailed comparison of Manali vs Shimla for a 4-day trip with cost breakdown' },
    { icon: 'terrain', title: 'Spiti Valley', prompt: 'Complete Spiti Valley guide with route, permits, best time and things to carry' },
    { icon: 'restaurant', title: 'Delhi Street Food', prompt: 'Top 20 street food spots in Delhi with must-try dishes and locations' },
    { icon: 'umbrella', title: 'Rainforest Trips', prompt: 'Best rainforest and jungle stay experiences in India with wildlife encounters' },
    { icon: 'compare', title: 'Goa vs Kerala', prompt: 'Detailed comparison of Goa vs Kerala for a beach vacation with budget' },
    { icon: 'terrain', title: 'Meghalaya Guide', prompt: 'Complete Meghalaya travel guide with living root bridges, caves and waterfalls' },
    { icon: 'restaurant', title: 'Chennai Food', prompt: 'Best South Indian food in Chennai — filter coffee, dosa spots and banana leaf meals' },
    { icon: 'umbrella', title: 'Valley of Flowers', prompt: 'Guide to visiting Valley of Flowers in Uttarakhand with trek details and permits' },
    { icon: 'compare', title: 'Leh vs Spiti', prompt: 'Compare Ladakh vs Spiti Valley for a motorcycle trip with route and difficulty' },
    { icon: 'terrain', title: 'Andaman Guide', prompt: 'Complete Andaman Islands guide with island hopping, water activities and budget' },
    { icon: 'restaurant', title: 'Kolkata Food', prompt: 'Must-try Kolkata street food — puchka, kathi rolls and mishti doi spots' },
    { icon: 'umbrella', title: 'Winter Trips', prompt: 'Best winter destinations in India for snow lovers with temperature details' },
    { icon: 'compare', title: 'Train vs Flight', prompt: 'Compare train vs flight for Mumbai to Delhi with time, cost and comfort analysis' },
    { icon: 'terrain', title: 'Uttarakhand Guide', prompt: 'Complete Uttarakhand guide covering Rishikesh, Mussoorie, Nainital and Chopta' },
    { icon: 'restaurant', title: 'Mumbai Food', prompt: 'Best Mumbai street food — vada pav, pav bhaji, and hidden food gems' },
  ];

  /* Seeded shuffle — same date always gives same result, different dates give different results */
  function seededShuffle(arr, seed) {
    const a = arr.slice();
    let s = seed;
    for (let i = a.length - 1; i > 0; i--) {
      s = (s * 16807 + 0) % 2147483647;
      const j = s % (i + 1);
      [a[i], a[j]] = [a[j], a[i]];
    }
    return a;
  }

  function getDailySeed() {
    const d = new Date();
    return d.getFullYear() * 10000 + (d.getMonth() + 1) * 100 + d.getDate();
  }

  function getDailyContent() {
    const seed = getDailySeed();
    return {
      suggestions: seededShuffle(SUGGESTION_POOL, seed).slice(0, 6),
      chips: seededShuffle(CHIP_POOL, seed + 1).slice(0, 8),
      guides: seededShuffle(GUIDE_POOL, seed + 2).slice(0, 4),
    };
  }

  function renderDailyWelcome() {
    const daily = getDailyContent();

    DOM.suggestions.innerHTML = daily.suggestions.map(s => `
      <button class="saw-suggestion" data-prompt="${escapeHTML(s.prompt)}">
        <span class="material-symbols-outlined">${s.icon}</span>
        <div class="saw-suggestion-text">
          <strong>${escapeHTML(s.title)}</strong>
          <small>${escapeHTML(s.desc)}</small>
        </div>
      </button>
    `).join('');

    const chipsEl = DOM.welcome.querySelector('.saw-chips');
    if (chipsEl) {
      chipsEl.innerHTML = daily.chips.map(c => `
        <button class="saw-chip" data-prompt="${escapeHTML(c.prompt)}">
          <span class="material-symbols-outlined">${c.icon}</span> ${escapeHTML(c.label)}
        </button>
      `).join('');
    }

    const quickGrid = DOM.welcome.querySelector('.saw-quick-grid');
    if (quickGrid) {
      quickGrid.innerHTML = daily.guides.map(g => `
        <button class="saw-quick-card" data-prompt="${escapeHTML(g.prompt)}">
          <span class="material-symbols-outlined">${g.icon}</span>
          <strong>${escapeHTML(g.title)}</strong>
        </button>
      `).join('');
    }
  }

  /* ── Markdown Renderer ───────────────────── */
  function renderMarkdown(text) {
    if (!text) return '';
    let html = text;

    html = html.replace(/```(\w*)\n([\s\S]*?)```/g, (_, lang, code) => {
      const escaped = code.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
      return `<pre><code class="lang-${lang||'text'}">${escaped}</code><button class="saw-copy-code" onclick="window._sawCopyCode(this)"><span class="material-symbols-outlined">content_copy</span></button></pre>`;
    });

    html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
    html = html.replace(/\*\*\*(.+?)\*\*\*/g, '<strong><em>$1</em></strong>');
    html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');
    html = html.replace(/^### (.+)$/gm, '<h3>$1</h3>');
    html = html.replace(/^## (.+)$/gm, '<h2>$1</h2>');
    html = html.replace(/^# (.+)$/gm, '<h1>$1</h1>');
    html = html.replace(/^---$/gm, '<hr>');
    html = html.replace(/^> (.+)$/gm, '<blockquote>$1</blockquote>');

    html = html.replace(/^\|(.+)\|\s*\n\|[-|\s:]+\|\s*\n((?:\|.+\|\s*\n?)*)/gm, (_, header, body) => {
      const ths = header.split('|').filter(s=>s.trim()).map(s=>`<th>${s.trim()}</th>`).join('');
      const rows = body.trim().split('\n').map(row => {
        const tds = row.split('|').filter(s=>s.trim()).map(s=>`<td>${s.trim()}</td>`).join('');
        return `<tr>${tds}</tr>`;
      }).join('');
      return `<table><thead><tr>${ths}</tr></thead><tbody>${rows}</tbody></table>`;
    });

    html = html.replace(/^(?:- (.+)\n?)+/gm, (block) => {
      const items = block.trim().split('\n').map(l => `<li>${l.replace(/^- /,'')}</li>`).join('');
      return `<ul>${items}</ul>`;
    });

    html = html.replace(/^(?:\d+\. (.+)\n?)+/gm, (block) => {
      const items = block.trim().split('\n').map(l => `<li>${l.replace(/^\d+\. /,'')}</li>`).join('');
      return `<ol>${items}</ol>`;
    });

    html = html.replace(/\n\n+/g, '</p><p>');
    html = html.replace(/\n/g, '<br>');
    html = '<p>' + html + '</p>';
    html = html.replace(/<p><\/p>/g, '');
    html = html.replace(/<p>(<h[1-3]>)/g, '$1');
    html = html.replace(/(<\/h[1-3]>)<\/p>/g, '$1');
    html = html.replace(/<p>(<ul>)/g, '$1');
    html = html.replace(/(<\/ul>)<\/p>/g, '$1');
    html = html.replace(/<p>(<ol>)/g, '$1');
    html = html.replace(/(<\/ol>)<\/p>/g, '$1');
    html = html.replace(/<p>(<pre>)/g, '$1');
    html = html.replace(/(<\/pre>)<\/p>/g, '$1');
    html = html.replace(/<p>(<table>)/g, '$1');
    html = html.replace(/(<\/table>)<\/p>/g, '$1');
    html = html.replace(/<p>(<blockquote>)/g, '$1');
    html = html.replace(/(<\/blockquote>)<\/p>/g, '$1');
    html = html.replace(/<p>(<hr>)/g, '$1');
    html = html.replace(/(<hr>)<\/p>/g, '$1');

    return html;
  }

  window._sawCopyCode = function(btn) {
    const code = btn.parentElement.querySelector('code');
    if (code) {
      navigator.clipboard.writeText(code.textContent).then(() => showToast('Code copied'));
    }
  };

  /* ── Utilities ───────────────────────────── */
  function showToast(msg) {
    DOM.toastText.textContent = msg;
    DOM.toast.classList.add('visible');
    setTimeout(() => DOM.toast.classList.remove('visible'), 2500);
  }

  function scrollToBottom() {
    requestAnimationFrame(() => {
      DOM.messages.scrollTop = DOM.messages.scrollHeight;
    });
  }

  function generateId() {
    return crypto.randomUUID ? crypto.randomUUID() : String(Date.now()) + Math.random().toString(16).slice(2);
  }

  function escapeHTML(str) {
    const d = document.createElement('div');
    d.textContent = str || '';
    return d.innerHTML;
  }

  /* ── Custom Modal ─────────────────────────── */
  function openModal({ title, body, inputVal, danger, inputPlaceholder }) {
    return new Promise((resolve) => {
      DOM.modalTitle.textContent = title;
      DOM.modalBody.textContent = body;
      DOM.modalConfirm.className = 'saw-modal-btn saw-modal-confirm' + (danger ? ' danger' : '');

      if (inputVal !== undefined && inputVal !== null) {
        DOM.modalInputWrap.classList.add('visible');
        DOM.modalInput.value = inputVal;
        DOM.modalInput.placeholder = inputPlaceholder || '';
        setTimeout(() => DOM.modalInput.focus(), 50);
      } else {
        DOM.modalInputWrap.classList.remove('visible');
      }

      DOM.modalOverlay.classList.add('open');

      function cleanup(result) {
        DOM.modalOverlay.classList.remove('open');
        DOM.modalCancel.removeEventListener('click', onCancel);
        DOM.modalConfirm.removeEventListener('click', onConfirm);
        DOM.modalClose.removeEventListener('click', onCancel);
        DOM.modalOverlay.removeEventListener('click', onOverlay);
        DOM.modalInput.removeEventListener('keydown', onKeydown);
        resolve(result);
      }

      function onCancel() { cleanup(null); }
      function onConfirm() {
        cleanup(inputVal !== undefined && inputVal !== null ? DOM.modalInput.value : true);
      }
      function onOverlay(e) { if (e.target === DOM.modalOverlay) cleanup(null); }
      function onKeydown(e) {
        if (e.key === 'Enter') { e.preventDefault(); onConfirm(); }
        if (e.key === 'Escape') { e.preventDefault(); cleanup(null); }
      }

      DOM.modalCancel.addEventListener('click', onCancel);
      DOM.modalConfirm.addEventListener('click', onConfirm);
      DOM.modalClose.addEventListener('click', onCancel);
      DOM.modalOverlay.addEventListener('click', onOverlay);
      DOM.modalInput.addEventListener('keydown', onKeydown);
    });
  }

  function showConfirm(title, message, danger) {
    return openModal({ title, body: message, danger });
  }

  function showPromptModal(title, message, defaultValue, placeholder) {
    return openModal({ title, body: message, inputVal: defaultValue || '', inputPlaceholder: placeholder || '' });
  }

  /* ── API Calls ───────────────────────────── */
  async function apiSend(message, sessionId, files) {
    const body = { message, session_id: sessionId, my_trip_connected: state.myTripConnected, my_trip_scope: state.myTripScope };
    if (files && files.length > 0) {
      const file = files[0];
      const b64 = await fileToBase64(file);
      body.image_base64 = b64.split(',')[1];
      body.image_mime = file.type || 'image/jpeg';
      body.image_name = file.name;
    }
    const res = await fetch('/api/chat/send', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    if (!res.ok) {
      if (res.status === 401 || res.status === 403) {
        window.location.href = '/login';
        return null;
      }
      throw new Error('Server error ' + res.status);
    }
    return res.json();
  }

  async function apiGetSessions() {
    const res = await fetch('/api/chat/sessions');
    if (!res.ok) return [];
    return res.json();
  }

  async function apiGetMessages(sessionId) {
    const res = await fetch('/api/chat/session/' + sessionId);
    if (!res.ok) return [];
    return res.json();
  }

  async function apiDeleteSession(sessionId) {
    await fetch('/api/chat/session/' + sessionId, { method: 'DELETE' });
  }

  async function apiRenameSession(sessionId, title) {
    await fetch('/api/chat/session/' + sessionId + '/title', {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title }),
    });
  }

  async function apiPinSession(sessionId) {
    await fetch('/api/chat/session/' + sessionId + '/pin', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({}),
    });
  }

  async function apiClearAll() {
    await fetch('/api/chat/sessions/clear', { method: 'POST' });
  }

  /* ── My Trip Connection ──────────────────── */
  function loadMyTripState() {
    try {
      const saved = localStorage.getItem('saw_mytrip_connected');
      state.myTripConnected = saved === 'true';
    } catch (e) {
      state.myTripConnected = false;
    }
    loadScopeState();
    renderMyTripUI();
  }

  function saveMyTripState() {
    try {
      localStorage.setItem('saw_mytrip_connected', String(state.myTripConnected));
    } catch (e) {}
  }

  function renderMyTripUI() {
    if (!DOM.mytripBtn || !DOM.mytripStatus) return;
    if (state.myTripConnected) {
      DOM.mytripBtn.classList.add('connected');
      DOM.mytripBtn.querySelector('.saw-mytrip-btn-label').textContent = 'Disconnect My Trip';
      DOM.mytripBtn.querySelector('.material-symbols-outlined').textContent = 'link_off';
      DOM.mytripBtn.title = 'Disconnect your trips and destinations from the AI assistant';
      DOM.mytripStatus.className = 'saw-mytrip-status visible connected';
      DOM.mytripStatus.innerHTML = '<span class="material-symbols-outlined">check_circle</span> Connected to My Trip';
    } else {
      DOM.mytripBtn.classList.remove('connected');
      DOM.mytripBtn.querySelector('.saw-mytrip-btn-label').textContent = 'Connect My Trip';
      DOM.mytripBtn.querySelector('.material-symbols-outlined').textContent = 'trip_origin';
      DOM.mytripBtn.title = 'Connect your saved trips and destinations to the AI assistant';
      DOM.mytripStatus.className = 'saw-mytrip-status';
      DOM.mytripStatus.innerHTML = '';
      state.myTripScope = null;
      saveScopeState();
    }
    renderScopeBar();
  }

  function loadScopeState() {
    try {
      const saved = localStorage.getItem('saw_mytrip_scope');
      if (saved === 'trips' || saved === 'destinations') {
        state.myTripScope = saved;
      } else {
        state.myTripScope = null;
      }
    } catch (e) {
      state.myTripScope = null;
    }
  }

  function saveScopeState() {
    try {
      if (state.myTripScope) {
        localStorage.setItem('saw_mytrip_scope', state.myTripScope);
      } else {
        localStorage.removeItem('saw_mytrip_scope');
      }
    } catch (e) {}
  }

  function renderScopeBar() {
    if (!DOM.scopeBar) return;
    if (state.myTripConnected) {
      DOM.scopeBar.classList.add('visible');
      updateScopePills();
    } else {
      DOM.scopeBar.classList.remove('visible');
    }
  }

  function updateScopePills() {
    if (DOM.scopeTrips) {
      DOM.scopeTrips.classList.toggle('active', state.myTripScope === 'trips');
    }
    if (DOM.scopeDestinations) {
      DOM.scopeDestinations.classList.toggle('active', state.myTripScope === 'destinations');
    }
    // Update placeholder
    if (DOM.input) {
      if (state.myTripScope === 'trips') {
        DOM.input.placeholder = 'Ask about your trips... (Plan a Trip)';
      } else if (state.myTripScope === 'destinations') {
        DOM.input.placeholder = 'Ask about your destinations... (Explore Destination)';
      } else {
        DOM.input.placeholder = 'Plan a trip, compare destinations, or ask anything...';
      }
    }
  }

  function setScope(scope) {
    if (state.myTripScope === scope) {
      // Toggle off
      state.myTripScope = null;
    } else {
      state.myTripScope = scope;
    }
    saveScopeState();
    updateScopePills();
  }

  async function toggleMyTripConnection() {
    if (state.myTripConnected) {
      state.myTripConnected = false;
      saveMyTripState();
      renderMyTripUI();
      showToast('My Trip disconnected from AI assistant');
    } else {
      DOM.mytripBtn.disabled = true;
      DOM.mytripBtn.querySelector('.saw-mytrip-btn-label').textContent = 'Connecting...';
      try {
        const res = await fetch('/api/my-trip-context');
        if (res.ok) {
          const data = await res.json();
          const hasData = (data.trips && data.trips.length > 0) ||
                          (data.saved_destinations && data.saved_destinations.length > 0) ||
                          (data.favorite_destinations && data.favorite_destinations.length > 0);
          state.myTripConnected = true;
          saveMyTripState();
          renderMyTripUI();
          if (hasData) {
            const parts = [];
            if (data.trips && data.trips.length > 0) parts.push(data.trips.length + ' trip' + (data.trips.length > 1 ? 's' : ''));
            if (data.saved_destinations && data.saved_destinations.length > 0) parts.push(data.saved_destinations.length + ' saved destination' + (data.saved_destinations.length > 1 ? 's' : ''));
            if (data.favorite_destinations && data.favorite_destinations.length > 0) parts.push(data.favorite_destinations.length + ' favorite' + (data.favorite_destinations.length > 1 ? 's' : ''));
            showToast('My Trip connected! (' + parts.join(', ') + ')');
          } else {
            showToast('My Trip connected! No saved trips or destinations found yet.');
          }
        } else {
          showToast('Failed to connect My Trip. Please try again.');
        }
      } catch (err) {
        console.error('My Trip connect error:', err);
        showToast('Failed to connect My Trip. Please try again.');
      } finally {
        DOM.mytripBtn.disabled = false;
      }
    }
  }

  function fileToBase64(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result);
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
  }

  /* ── Sidebar ─────────────────────────────── */
  async function loadSessions() {
    state.sessions = await apiGetSessions();
    renderSidebar();
  }

  function renderSidebar(filter) {
    const list = DOM.sidebarList;
    const filtered = filter
      ? state.sessions.filter(s => s.title.toLowerCase().includes(filter.toLowerCase()))
      : state.sessions;

    if (filtered.length === 0) {
      list.innerHTML = `
        <div class="saw-sidebar-empty">
          <span class="material-symbols-outlined">chat_bubble_outline</span>
          <p>${filter ? 'No matching conversations' : 'Start a new conversation'}</p>
        </div>`;
      return;
    }

    let html = '';
    const pinned = filtered.filter(s => s.pinned);
    const unpinned = filtered.filter(s => !s.pinned);

    if (pinned.length > 0) {
      html += '<div class="saw-sidebar-section"><div class="saw-sidebar-section-title">Pinned</div></div>';
      pinned.forEach(s => { html += sidebarItemHTML(s); });
    }
    if (unpinned.length > 0) {
      if (pinned.length > 0) {
        html += '<div class="saw-sidebar-section"><div class="saw-sidebar-section-title">Recent</div></div>';
      }
      unpinned.forEach(s => { html += sidebarItemHTML(s); });
    }

    list.innerHTML = html;

    $$('.saw-sidebar-item', list).forEach(el => {
      el.addEventListener('click', (e) => {
        if (e.target.closest('.saw-sidebar-item-more')) return;
        const id = parseInt(el.dataset.id);
        loadConversation(id);
      });
    });

    $$('.saw-sidebar-item-more', list).forEach(el => {
      el.addEventListener('click', (e) => {
        e.stopPropagation();
        const id = parseInt(el.closest('.saw-sidebar-item').dataset.id);
        showItemMenu(e, id);
      });
    });
  }

  function sidebarItemHTML(s) {
    const active = s.id === state.sessionId ? ' active' : '';
    return `
      <div class="saw-sidebar-item${active}" data-id="${s.id}">
        <div class="saw-sidebar-item-icon">
          <span class="material-symbols-outlined">chat</span>
        </div>
        <div class="saw-sidebar-item-info">
          <div class="saw-sidebar-item-title">${escapeHTML(s.title)}</div>
          <div class="saw-sidebar-item-preview">${escapeHTML(s.last_message || '')}</div>
        </div>
        <button class="saw-sidebar-item-more" title="More options">
          <span class="material-symbols-outlined">more_horiz</span>
        </button>
      </div>`;
  }

  /* ── Item Menu (three-dot dropdown) ──────── */
  function showItemMenu(e, sessionId) {
    state.itemMenuTarget = sessionId;
    const menu = DOM.itemMenu;
    const session = state.sessions.find(s => s.id === sessionId);
    const pinBtn = menu.querySelector('[data-action="pin"]');
    if (session && pinBtn) {
      pinBtn.innerHTML = `<span class="material-symbols-outlined">push_pin</span> ${session.pinned ? 'Unpin' : 'Pin'}`;
    }

    const rect = e.target.getBoundingClientRect();
    let x = rect.right + 6;
    let y = rect.top - 4;
    if (x + 180 > window.innerWidth) x = rect.left - 180;
    if (y + 150 > window.innerHeight) y = window.innerHeight - 160;
    if (y < 0) y = 8;

    menu.style.left = x + 'px';
    menu.style.top = y + 'px';
    menu.classList.add('open');
  }

  function hideItemMenu() {
    DOM.itemMenu.classList.remove('open');
    state.itemMenuTarget = null;
  }

  /* ── Conversation Management ─────────────── */
  function newChat() {
    state.sessionId = null;
    DOM.msgContainer.innerHTML = '';
    DOM.welcome.classList.remove('hidden');
    DOM.input.value = '';
    DOM.input.style.height = 'auto';
    clearAttachments();
    updateSendBtn();
    renderSidebar();
    DOM.input.focus();
  }

  async function loadConversation(sessionId) {
    state.sessionId = sessionId;
    DOM.welcome.classList.add('hidden');
    DOM.msgContainer.innerHTML = '';

    const messages = await apiGetMessages(sessionId);
    messages.forEach(m => {
      appendMessage(m.role === 'ai' ? 'assistant' : m.role, m.content, false);
    });
    scrollToBottom();
    renderSidebar();
    closeSidebarOnMobile();
  }

  /* ── Message Rendering ───────────────────── */
  function appendMessage(role, text, animate) {
    const id = generateId();
    const isUser = role === 'user';
    const avatarIcon = isUser ? 'person' : 'auto_awesome';
    const bubbleClass = isUser ? 'user' : 'ai';

    const div = document.createElement('div');
    div.className = 'saw-msg' + (isUser ? ' user' : '');
    div.dataset.role = role;
    div.dataset.msgId = id;
    div.dataset.text = text;
    if (animate === false) div.style.animation = 'none';

    div.innerHTML = `
      ${isUser ? '' : `<div class="saw-msg-avatar">
        <span class="material-symbols-outlined">${avatarIcon}</span>
      </div>`}
      <div class="saw-msg-body">
        <div class="saw-bubble ${bubbleClass}">${isUser ? escapeHTML(text) : renderMarkdown(text)}</div>
        <div class="saw-msg-actions">
          ${isUser ? `
          <button class="saw-msg-act" data-action="edit" title="Edit">
            <span class="material-symbols-outlined">edit</span>
          </button>
          <button class="saw-msg-act" data-action="copy" title="Copy">
            <span class="material-symbols-outlined">content_copy</span>
          </button>
          <button class="saw-msg-act" data-action="share" title="Share">
            <span class="material-symbols-outlined">share</span>
          </button>
          ` : `
          <button class="saw-msg-act" data-action="copy" title="Copy">
            <span class="material-symbols-outlined">content_copy</span>
          </button>
          <button class="saw-msg-act" data-action="share" title="Share">
            <span class="material-symbols-outlined">share</span>
          </button>
          <button class="saw-msg-act" data-action="regenerate" title="Regenerate">
            <span class="material-symbols-outlined">refresh</span>
          </button>
          <button class="saw-msg-act" data-action="more" title="More">
            <span class="material-symbols-outlined">more_horiz</span>
          </button>
          `}
        </div>
      </div>`;

    DOM.msgContainer.appendChild(div);

    $$('.saw-msg-act', div).forEach(btn => {
      btn.addEventListener('click', (e) => {
        handleMsgAction(btn.dataset.action, div, e);
      });
    });

    if (animate !== false) scrollToBottom();
    return div;
  }

  function handleMsgAction(action, msgEl, event) {
    const text = msgEl.dataset.text || '';
    const role = msgEl.dataset.role;

    switch (action) {
      case 'copy':
        navigator.clipboard.writeText(text).then(() => showToast('Copied to clipboard'));
        break;
      case 'share':
        navigator.clipboard.writeText(text).then(() => showToast('Copied for sharing'));
        break;
      case 'edit':
        if (role === 'user') enterEditMode(msgEl);
        break;
      case 'regenerate':
        if (role === 'assistant') regenerateLastResponse();
        break;
      case 'more':
        state.contextTarget = { role, text, msgEl };
        showContextMenu(event);
        break;
    }
  }

  /* ── Edit Mode ───────────────────────────── */
  let editingMsg = null;

  function enterEditMode(msgEl) {
    editingMsg = msgEl;
    const text = msgEl.dataset.text || '';
    DOM.input.value = text;
    autoResize();
    updateSendBtn();
    DOM.composerBox.classList.add('editing');
    DOM.input.focus();
    DOM.messages.scrollTop = DOM.messages.scrollTop;
  }

  function exitEditMode() {
    editingMsg = null;
    DOM.input.value = '';
    DOM.input.style.height = 'auto';
    DOM.composerBox.classList.remove('editing');
    updateSendBtn();
  }

  async function regenerateLastResponse() {
    const aiMsgs = $$('.saw-msg[data-role="assistant"]', DOM.msgContainer);
    if (aiMsgs.length === 0) return;
    aiMsgs[aiMsgs.length - 1].remove();

    const userMsgs = $$('.saw-msg[data-role="user"]', DOM.msgContainer);
    if (userMsgs.length === 0) return;

    await sendMessageToAI(userMsgs[userMsgs.length - 1].dataset.text);
  }

  async function handleSend() {
    const text = DOM.input.value.trim();
    if (state.isTyping || (!text && state.pendingFiles.length === 0)) return;

    DOM.welcome.classList.add('hidden');

    if (editingMsg) {
      const oldMsg = editingMsg;
      editingMsg = null;
      DOM.composerBox.classList.remove('editing');

      oldMsg.querySelector('.saw-bubble').textContent = text;
      oldMsg.dataset.text = text;

      const nextSibling = oldMsg.nextElementSibling;
      if (nextSibling && nextSibling.dataset.role === 'assistant') {
        nextSibling.remove();
      }

      DOM.input.value = '';
      DOM.input.style.height = 'auto';
      clearAttachments();
      updateSendBtn();

      state.isTyping = true;
      DOM.typing.classList.add('visible');
      scrollToBottom();
      try {
        const data = await apiSend(text, state.sessionId, state.pendingFiles);
        if (!data) return;
        state.sessionId = data.session_id;
        DOM.typing.classList.remove('visible');
        appendMessage('assistant', data.response || 'No response received.', true);
        if (data.session_id) {
          const sessions = await apiGetSessions();
          state.sessions = sessions;
          renderSidebar();
        }
      } catch (err) {
        console.error('Send error:', err);
        DOM.typing.classList.remove('visible');
        appendMessage('assistant', 'Sorry, something went wrong. Please try again.', true);
      } finally {
        state.isTyping = false;
        clearAttachments();
      }
      return;
    }

    const displayText = text || (state.pendingFiles.length > 0 ? '[Image attached]' : '');
    appendMessage('user', displayText, true);

    DOM.input.value = '';
    DOM.input.style.height = 'auto';
    clearAttachments();
    updateSendBtn();

    await sendMessageToAI(text);
  }

  async function sendMessageToAI(text) {
    state.isTyping = true;
    DOM.typing.classList.add('visible');
    scrollToBottom();

    try {
      const data = await apiSend(text, state.sessionId, state.pendingFiles);
      if (!data) return;

      state.sessionId = data.session_id;
      DOM.typing.classList.remove('visible');

      appendMessage('assistant', data.response || 'No response received.', true);

      if (data.session_id) {
        const sessions = await apiGetSessions();
        state.sessions = sessions;
        renderSidebar();
      }
    } catch (err) {
      console.error('Send error:', err);
      DOM.typing.classList.remove('visible');
      appendMessage('assistant', 'Sorry, something went wrong. Please try again.', true);
    } finally {
      state.isTyping = false;
      clearAttachments();
    }
  }

  /* ── Composer ────────────────────────────── */
  function autoResize() {
    const el = DOM.input;
    el.style.height = 'auto';
    el.style.height = Math.min(el.scrollHeight, 150) + 'px';
  }

  function updateSendBtn() {
    const hasText = DOM.input.value.trim().length > 0;
    const hasFiles = state.pendingFiles.length > 0;
    if (hasText || hasFiles) {
      DOM.sendBtn.classList.add('active');
      DOM.sendBtn.style.cursor = 'pointer';
    } else {
      DOM.sendBtn.classList.remove('active');
      DOM.sendBtn.style.cursor = 'not-allowed';
    }
  }

  /* ── File Attachments ────────────────────── */
  function handleFileSelect(files) {
    for (const file of files) {
      if (state.pendingFiles.length >= 5) break;
      state.pendingFiles.push(file);
    }
    renderAttachments();
    updateSendBtn();
  }

  function renderAttachments() {
    DOM.attachments.innerHTML = state.pendingFiles.map((f, i) => {
      const isImg = f.type.startsWith('image/');
      return `
        <div class="saw-attachment-preview">
          ${isImg ? `<img src="${URL.createObjectURL(f)}" alt="">` : `<span class="material-symbols-outlined" style="font-size:18px;">description</span>`}
          <span>${f.name.length > 20 ? f.name.slice(0,20)+'...' : f.name}</span>
          <button class="saw-attachment-remove" data-idx="${i}">&times;</button>
        </div>`;
    }).join('');

    $$('.saw-attachment-remove', DOM.attachments).forEach(btn => {
      btn.addEventListener('click', () => {
        state.pendingFiles.splice(parseInt(btn.dataset.idx), 1);
        renderAttachments();
        updateSendBtn();
      });
    });
  }

  function clearAttachments() {
    state.pendingFiles = [];
    DOM.attachments.innerHTML = '';
  }

  /* ── Voice Input ─────────────────────────── */
  function toggleVoice() {
    if (!('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)) {
      showToast('Voice input not supported in this browser');
      return;
    }

    if (state.isRecording) {
      if (state.recognition) state.recognition.stop();
      state.isRecording = false;
      DOM.voiceBtn.classList.remove('recording');
      return;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    state.recognition = new SpeechRecognition();
    state.recognition.lang = 'en-US';
    state.recognition.interimResults = false;
    state.recognition.maxAlternatives = 1;

    state.recognition.onresult = (event) => {
      DOM.input.value = event.results[0][0].transcript;
      autoResize();
      updateSendBtn();
    };

    state.recognition.onend = () => { state.isRecording = false; DOM.voiceBtn.classList.remove('recording'); };
    state.recognition.onerror = () => { state.isRecording = false; DOM.voiceBtn.classList.remove('recording'); };

    state.recognition.start();
    state.isRecording = true;
    DOM.voiceBtn.classList.add('recording');
    showToast('Listening...');
  }

  /* ── Context Menu (message actions) ──────── */
  function showContextMenu(e) {
    const menu = DOM.contextMenu;

    if (DOM.readAloudBtn) {
      if (state.isSpeaking) {
        DOM.readAloudBtn.innerHTML = '<span class="material-symbols-outlined">stop</span> Stop Reading';
      } else {
        DOM.readAloudBtn.innerHTML = '<span class="material-symbols-outlined">volume_up</span> Read Aloud';
      }
    }

    menu.classList.add('open');
    const x = Math.min(e.clientX || e.pageX, window.innerWidth - 220);
    const y = Math.min(e.clientY || e.pageY, window.innerHeight - 320);
    menu.style.left = x + 'px';
    menu.style.top = y + 'px';
  }

  function hideContextMenu() {
    DOM.contextMenu.classList.remove('open');
  }

  /* ── Share Chat ───────────────────────────── */
  async function shareChat(sessionId) {
    const session = state.sessions.find(s => s.id === sessionId);
    const title = session ? session.title : 'Chat';

    showToast('Preparing share...');

    try {
      const messages = await apiGetMessages(sessionId);
      if (!messages || messages.length === 0) {
        showToast('No messages to share');
        return;
      }

      let text = '=== ' + title + ' ===\n\n';
      messages.forEach(m => {
        const role = m.role === 'ai' ? 'Skupheon AI' : 'You';
        text += role + ':\n' + m.content + '\n\n';
      });
      text += '--- Shared from Skupheon AI ---';

      if (navigator.share) {
        try {
          await navigator.share({ title: title, text: text });
          showToast('Chat shared');
          return;
        } catch (err) {
          if (err.name === 'AbortError') return;
        }
      }

      await navigator.clipboard.writeText(text);
      showToast('Chat copied to clipboard');
    } catch (err) {
      showToast('Failed to share chat');
    }
  }

  /* ── Drag and Drop ───────────────────────── */
  function initDragDrop() {
    const chat = $('#saw-chat');
    let dragCounter = 0;

    chat.addEventListener('dragenter', (e) => { e.preventDefault(); dragCounter++; DOM.dropOverlay.classList.add('active'); });
    chat.addEventListener('dragleave', (e) => { e.preventDefault(); dragCounter--; if (dragCounter === 0) DOM.dropOverlay.classList.remove('active'); });
    chat.addEventListener('dragover', (e) => e.preventDefault());
    chat.addEventListener('drop', (e) => {
      e.preventDefault();
      dragCounter = 0;
      DOM.dropOverlay.classList.remove('active');
      if (e.dataTransfer.files.length > 0) handleFileSelect(e.dataTransfer.files);
    });
  }

  /* ── Sidebar Toggle ──────────────────────── */
  function closeSidebarOnMobile() {
    if (window.innerWidth <= 860) DOM.sidebar.classList.add('collapsed');
  }

  /* ── Init ────────────────────────────────── */
  function init() {
    DOM.sendBtn.addEventListener('click', handleSend);

    DOM.input.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend(); }
    });

    DOM.input.addEventListener('input', () => { autoResize(); updateSendBtn(); });

    DOM.newChatBtn.addEventListener('click', newChat);

    DOM.sidebarSearch.addEventListener('input', (e) => renderSidebar(e.target.value));

    DOM.clearAllBtn.addEventListener('click', async () => {
      const ok = await showConfirm('Clear All', 'Delete all conversations? This cannot be undone.', true);
      if (ok) {
        await apiClearAll();
        newChat();
        await loadSessions();
        showToast('All conversations cleared');
      }
    });

    DOM.attachBtn.addEventListener('click', () => DOM.fileInput.click());
    DOM.fileInput.addEventListener('change', (e) => { handleFileSelect(e.target.files); DOM.fileInput.value = ''; });

    DOM.voiceBtn.addEventListener('click', toggleVoice);

    DOM.editCancel.addEventListener('click', exitEditMode);
    DOM.editResend.addEventListener('click', () => { handleSend(); });

    DOM.input.addEventListener('paste', (e) => {
      const items = e.clipboardData.items;
      const imageFiles = [];
      for (const item of items) {
        if (item.type.startsWith('image/')) imageFiles.push(item.getAsFile());
      }
      if (imageFiles.length > 0) { e.preventDefault(); handleFileSelect(imageFiles); }
    });

    document.addEventListener('click', (e) => {
      const suggestion = e.target.closest('.saw-suggestion, .saw-chip, .saw-quick-card');
      if (suggestion) {
        const prompt = suggestion.dataset.prompt;
        if (prompt) {
          DOM.input.value = prompt;
          autoResize();
          updateSendBtn();
          handleSend();
        }
      }
    });

    document.addEventListener('click', (e) => {
      if (!e.target.closest('.saw-context-menu') && !e.target.closest('[data-action="more"]')) hideContextMenu();
      if (!e.target.closest('.saw-item-menu') && !e.target.closest('.saw-sidebar-item-more')) hideItemMenu();
    });

    $$('.saw-context-item', DOM.contextMenu).forEach(item => {
      item.addEventListener('click', () => {
        const action = item.dataset.action;
        const target = state.contextTarget;
        hideContextMenu();
        if (!target) return;

        switch (action) {
          case 'read-aloud': {
            if (!('speechSynthesis' in window)) break;
            const msgText = target.text || '';
            if (state.isSpeaking) {
              window.speechSynthesis.cancel();
              state.isSpeaking = false;
              state.speakingMsgEl = null;
              DOM.readAloudBtn.innerHTML = '<span class="material-symbols-outlined">volume_up</span> Read Aloud';
            } else {
              window.speechSynthesis.cancel();
              const u = new SpeechSynthesisUtterance(msgText);
              u.rate = 1;
              u.pitch = 1;
              u.onend = () => {
                state.isSpeaking = false;
                state.speakingMsgEl = null;
              };
              u.onerror = () => {
                state.isSpeaking = false;
                state.speakingMsgEl = null;
              };
              window.speechSynthesis.speak(u);
              state.isSpeaking = true;
              state.speakingMsgEl = target.msgEl;
            }
            break;
          }
          case 'delete':
            target.msgEl.remove();
            showToast('Message deleted');
            break;
        }
      });
    });

    $$('.saw-item-menu-item', DOM.itemMenu).forEach(item => {
      item.addEventListener('click', async () => {
        const action = item.dataset.action;
        const id = state.itemMenuTarget;
        hideItemMenu();
        if (!id) return;

        switch (action) {
          case 'rename': {
            const session = state.sessions.find(s => s.id === id);
            const newTitle = await showPromptModal('Rename', 'Enter a new name for this conversation:', session ? session.title : '', 'Conversation name');
            if (newTitle && newTitle.trim()) {
              await apiRenameSession(id, newTitle.trim());
              await loadSessions();
              showToast('Renamed');
            }
            break;
          }
          case 'pin':
            await apiPinSession(id);
            await loadSessions();
            showToast('Updated');
            break;
          case 'share':
            await shareChat(id);
            break;
          case 'delete': {
            const ok = await showConfirm('Delete Conversation', 'Are you sure you want to delete this conversation?', true);
            if (ok) {
              await apiDeleteSession(id);
              if (state.sessionId === id) {
                state.sessionId = null;
                newChat();
              }
              await loadSessions();
              showToast('Conversation deleted');
            }
            break;
          }
        }
      });
    });

    initDragDrop();

    document.addEventListener('keydown', (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        DOM.sidebarSearch.focus();
        if (DOM.sidebar.classList.contains('collapsed')) DOM.sidebar.classList.remove('collapsed');
      }
      if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'N') {
        e.preventDefault();
        newChat();
      }
      if (e.key === 'Escape') {
        hideContextMenu();
        hideItemMenu();
      }
    });

    loadSessions();
    renderDailyWelcome();

    loadMyTripState();
    if (DOM.mytripBtn) {
      DOM.mytripBtn.addEventListener('click', toggleMyTripConnection);
    }
    if (DOM.scopeTrips) {
      DOM.scopeTrips.addEventListener('click', () => setScope('trips'));
    }
    if (DOM.scopeDestinations) {
      DOM.scopeDestinations.addEventListener('click', () => setScope('destinations'));
    }

    if (window.innerWidth <= 860) DOM.sidebar.classList.add('collapsed');
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
