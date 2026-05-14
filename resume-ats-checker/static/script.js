// script.js
// Frontend logic for Resume ATS Checker

let selectedFile = null;

// ===== FILE HANDLING =====
function handleFile(input) {
  const file = input.files[0];
  if (!file) return;
  selectedFile = file;
  document.getElementById('dropZone').style.display    = 'none';
  document.getElementById('fileSelected').style.display = 'flex';
  document.getElementById('fileName').textContent       = file.name;
}

function clearFile() {
  selectedFile = null;
  document.getElementById('resumeFile').value           = '';
  document.getElementById('dropZone').style.display    = 'block';
  document.getElementById('fileSelected').style.display = 'none';
}

// ===== DRAG AND DROP =====
const dropZone = document.getElementById('dropZone');
dropZone.addEventListener('dragover',  e => { e.preventDefault(); dropZone.classList.add('dragover'); });
dropZone.addEventListener('dragleave', ()=> { dropZone.classList.remove('dragover'); });
dropZone.addEventListener('drop', e => {
  e.preventDefault();
  dropZone.classList.remove('dragover');
  const file = e.dataTransfer.files[0];
  if (file) {
    selectedFile = file;
    document.getElementById('dropZone').style.display    = 'none';
    document.getElementById('fileSelected').style.display = 'flex';
    document.getElementById('fileName').textContent       = file.name;
  }
});

// ===== ANALYZE =====
async function analyzeResume() {
  if (!selectedFile) { alert('Please upload your resume first!'); return; }
  const jobRole = document.getElementById('jobRole').value;
  if (!jobRole) { alert('Please select a job role!'); return; }

  // Show loading
  const btn = document.getElementById('analyzeBtn');
  btn.classList.add('loading');
  btn.innerHTML = '<i class="ti ti-loader ti-spin"></i> Analyzing...';
  document.getElementById('placeholder').style.display   = 'none';
  document.getElementById('loading').style.display       = 'flex';
  document.getElementById('loading').style.flexDirection = 'column';
  document.getElementById('resultContent').style.display = 'none';

  // Build form data
  const formData = new FormData();
  formData.append('resume',   selectedFile);
  formData.append('job_role', jobRole);

  try {
    const res  = await fetch('/analyze', { method: 'POST', body: formData });
    const data = await res.json();

    document.getElementById('loading').style.display = 'none';

    if (!data.success) {
      alert(data.message);
      document.getElementById('placeholder').style.display = 'block';
    } else {
      showResults(data.result);
    }
  } catch (err) {
    document.getElementById('loading').style.display    = 'none';
    document.getElementById('placeholder').style.display = 'block';
    alert('Something went wrong. Please try again.');
  }

  btn.classList.remove('loading');
  btn.innerHTML = '<i class="ti ti-search"></i> <span>Analyze Resume</span>';
}

// ===== SHOW RESULTS =====
function showResults(r) {
  document.getElementById('resultContent').style.display = 'block';

  // Score circle animation
  const circle       = document.getElementById('scoreCircle');
  const circumference = 264;
  const offset        = circumference - (circumference * r.overall_score / 100);
  circle.style.strokeDashoffset = offset;

  // Color based on score
  const color = r.overall_score >= 80 ? '#1D9E75'
              : r.overall_score >= 60 ? '#7F77DD'
              : r.overall_score >= 40 ? '#BA7517'
              : '#E24B4A';
  circle.style.stroke = color;

  // Fill numbers
  animateNumber('scoreNum', r.overall_score);
  document.getElementById('scoreRole').textContent    = r.job_role;
  document.getElementById('roleScore').textContent    = r.role_score + '%';
  document.getElementById('generalScore').textContent = r.general_score + '%';
  document.getElementById('wordCount').textContent    = r.word_count;

  // Grade badge
  const badge = document.getElementById('gradeBadge');
  badge.textContent = r.grade;
  badge.style.background = r.overall_score >= 80 ? '#E1F5EE'
                         : r.overall_score >= 60 ? '#EEEDFE'
                         : r.overall_score >= 40 ? '#FAEEDA'
                         : '#FCEBEB';
  badge.style.color = color;
  document.getElementById('gradeMsg').textContent = r.message;

  // Keywords found
  const foundDiv = document.getElementById('keywordsFound');
  foundDiv.innerHTML = r.role_found.length
    ? r.role_found.map(k => `<span class="kw-tag found"><i class="ti ti-check"></i>${k}</span>`).join('')
    : '<p style="color:var(--muted);font-size:14px">No matching keywords found</p>';

  // Keywords missing
  const missingDiv = document.getElementById('keywordsMissing');
  missingDiv.innerHTML = r.role_missing.length
    ? r.role_missing.map(k => `<span class="kw-tag missing"><i class="ti ti-plus"></i>${k}</span>`).join('')
    : '<p style="color:var(--green);font-size:14px">✅ No major keywords missing!</p>';

  // Suggestions
  const suggDiv = document.getElementById('suggestionsList');
  suggDiv.innerHTML = r.suggestions.map(s => `<li>${s}</li>`).join('');

  // Scroll to results
  document.getElementById('resultContent').scrollIntoView({ behavior: 'smooth' });
}

// ===== ANIMATE NUMBER =====
function animateNumber(id, target) {
  let current  = 0;
  const el     = document.getElementById(id);
  const step   = target / 40;
  const timer  = setInterval(() => {
    current += step;
    if (current >= target) { current = target; clearInterval(timer); }
    el.textContent = Math.round(current);
  }, 30);
}
