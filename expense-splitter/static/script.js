// script.js
// Handles all frontend interactions

// ===== ADD MEMBER =====
async function addMember() {
  const name  = document.getElementById('memberName').value.trim();
  const phone = document.getElementById('memberPhone').value.trim();
  if (!name || !phone) { log('Please enter name and phone', 'err'); return; }

  const res  = await fetch('/add_member', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, phone })
  });
  const data = await res.json();

  if (data.success) {
    log(`Member added: ${name}`);
    document.getElementById('memberName').value  = '';
    document.getElementById('memberPhone').value = '';
    renderMembers(data.members);
  } else {
    log(data.message, 'err');
  }
}

// ===== ADD EXPENSE =====
async function addExpense() {
  const paid_by     = document.getElementById('paidBy').value;
  const amount      = document.getElementById('amount').value;
  const description = document.getElementById('description').value.trim();
  if (!paid_by || !amount || !description) { log('Fill all expense fields', 'err'); return; }

  const res  = await fetch('/add_expense', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ paid_by, amount, description })
  });
  const data = await res.json();

  if (data.success) {
    log(`Expense added: ₹${amount} by ${paid_by} for ${description}`);
    document.getElementById('amount').value      = '';
    document.getElementById('description').value = '';
    renderExpenses(data.expenses);
  } else {
    log(data.message, 'err');
  }
}

// ===== CALCULATE =====
async function calculate() {
  const res  = await fetch('/calculate');
  const data = await res.json();

  if (!data.success) { log(data.message, 'err'); return; }

  const r    = data.result;
  let html   = `
    <div class="result-total">
      <div class="big">₹${r.total}</div>
      <div class="lbl">Total Bill — ₹${r.share} per person</div>
    </div>`;

  if (r.transactions.length === 0) {
    html += `<p class="settled">✅ Everyone is settled up!</p>`;
  } else {
    r.transactions.forEach(t => {
      html += `
        <div class="transaction">
          <span class="from">${t.from}</span>
          <i class="ti ti-arrow-right arrow"></i>
          <span class="to">${t.to}</span>
          <span class="amt">₹${t.amount}</span>
        </div>`;
    });
  }

  document.getElementById('resultArea').innerHTML = html;
  log(`Calculated! Total: ₹${r.total} | Per person: ₹${r.share}`);
}

// ===== SEND WHATSAPP =====
async function sendWhatsApp() {
  log('Sending WhatsApp messages...');
  const res  = await fetch('/send_whatsapp', { method: 'POST' });
  const data = await res.json();

  if (data.sent.length)   log(`Sent to: ${data.sent.join(', ')}`);
  if (data.failed.length) log(`Failed: ${data.failed.join(', ')}`, 'err');
}

// ===== RESET =====
async function resetAll() {
  if (!confirm('Reset everything?')) return;
  await fetch('/reset', { method: 'POST' });
  document.getElementById('memberList').innerHTML  = '';
  document.getElementById('expenseList').innerHTML = '';
  document.getElementById('resultArea').innerHTML  = '<p class="empty-msg">Add members and expenses to see the summary</p>';
  document.getElementById('paidBy').innerHTML      = '<option value="">Who paid?</option>';
  log('Reset done!');
}

// ===== RENDER MEMBERS =====
function renderMembers(members) {
  const list   = document.getElementById('memberList');
  const select = document.getElementById('paidBy');
  list.innerHTML   = members.map(m => `<span class="member-tag"><i class="ti ti-user"></i>${m.name}</span>`).join('');
  select.innerHTML = '<option value="">Who paid?</option>' +
    members.map(m => `<option value="${m.name}">${m.name}</option>`).join('');
}

// ===== RENDER EXPENSES =====
function renderExpenses(expenses) {
  const list = document.getElementById('expenseList');
  list.innerHTML = expenses.map(e => `
    <div class="expense-item">
      <div>
        <span class="expense-who">${e.paid_by}</span>
        <span class="expense-desc"> — ${e.description}</span>
      </div>
      <span class="expense-amt">₹${e.amount}</span>
    </div>`).join('');
}

// ===== STATUS LOG =====
function log(msg, type = 'ok') {
  const logDiv = document.getElementById('statusLog');
  const p      = document.createElement('p');
  p.className  = type === 'err' ? 'log-err' : 'log-msg';
  p.textContent = `> ${msg}`;
  logDiv.appendChild(p);
  logDiv.scrollTop = logDiv.scrollHeight;
}