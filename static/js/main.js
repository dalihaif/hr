/* 大理大学第一附属医院智能人事系统 - 前端逻辑 */
const API = '/api';
let currentUser = null;
let currentPage = 'dashboard';

// ============================================================
// 工具函数
// ============================================================
function fmt(n, decimals=2) { return Number(n||0).toFixed(decimals); }
function fmtMoney(n) { return '¥' + fmt(n); }
function tagClass(level) {
  const map = { 'A':'tag-success','B':'tag-primary','C':'tag-warning','D':'tag-danger','E':'tag-danger', '正高':'tag-success','副高':'tag-primary','中级':'tag-warning','初级':'tag-danger' };
  return map[level] || 'tag-primary';
}
function statusTag(status) {
  const map = { '在职':'tag-success','离职':'tag-danger','退休':'tag-warning','待审核':'tag-warning','已审核':'tag-success' };
  return `<span class="tag ${map[status]||'tag-primary'}">${status}</span>`;
}
function escHtml(s) { const d=document.createElement('div'); d.textContent=s||''; return d.innerHTML; }
function formatDate(d) { return d||'--'; }

async function apiFetch(path, opts={}) {
  const res = await fetch(API + path, { headers: {'Content-Type':'application/json'}, ...opts });
  if (res.status === 401) { showLogin(); return null; }
  return res.json();
}

// ============================================================
// 登录
// ============================================================
async function doLogin() {
  const u = document.getElementById('login-username').value;
  const p = document.getElementById('login-password').value;
  const res = await apiFetch('/login', { method:'POST', body: JSON.stringify({username:u, password:p}) });
  if (!res) return;
  if (res.error) { document.getElementById('login-error').textContent = res.error; return; }
  currentUser = res;
  document.getElementById('login-error').textContent = '';
  showApp();
}

async function checkSession() {
  const res = await apiFetch('/current_user');
  if (res && res.id) { currentUser = res; showApp(); }
  else { showLogin(); }
}

function showLogin() {
  document.getElementById('login-page').style.display = 'flex';
  document.getElementById('app-page').style.display = 'none';
}

function showApp() {
  document.getElementById('login-page').style.display = 'none';
  document.getElementById('app-page').style.display = '';
  document.getElementById('sidebar-user-name').textContent = currentUser.real_name;
  document.getElementById('sidebar-user-role').textContent = currentUser.role;
  loadPage('dashboard');
}

function logout() {
  apiFetch('/logout', {method:'POST'});
  currentUser = null;
  showLogin();
}

// ============================================================
// 页面导航
// ============================================================
function loadPage(page) {
  currentPage = page;
  document.querySelectorAll('.nav-item').forEach(n => n.classList.toggle('active', n.dataset.page === page));
  const titles = { dashboard:'系统概览', personnel:'人员信息管理', salary:'工资核算', performance:'绩效管理', settings:'系统设置' };
  document.getElementById('page-title').textContent = titles[page] || page;
  const loader = { dashboard:loadDashboard, personnel:loadPersonnel, salary:loadSalary, performance:loadPerformance, settings:loadSettings };
  (loader[page] || loadDashboard)();
}

// ============================================================
// Dashboard
// ============================================================
async function loadDashboard() {
  const emps = await apiFetch('/employees?per_page=1');
  const totalEmps = emps ? emps.total : 0;
  const activeEmps = await apiFetch('/employees?status=在职&per_page=1');
  const activeCount = activeEmps ? activeEmps.total : 0;
  
  let html = `<div class="metrics">
    <div class="metric"><div class="label">职工总数</div><div class="value primary">${totalEmps}</div></div>
    <div class="metric"><div class="label">在职人数</div><div class="value success">${activeCount}</div></div>
    <div class="metric"><div class="label">本月待核算</div><div class="value warning">--</div></div>
    <div class="metric"><div class="label">待评分考核</div><div class="value danger">--</div></div>
  </div>`;
  
  html += `<div class="card"><div class="card-header"><h3>科室人员分布</h3></div><div class="chart-container"><canvas id="deptChart" role="img" aria-label="科室人员分布图">Loading...</canvas></div></div>`;
  
  html += `<div class="card"><div class="card-header"><h3>最近操作记录</h3></div><div class="table-wrap"><table><thead><tr><th>时间</th><th>用户</th><th>操作</th><th>模块</th><th>详情</th></tr></thead><tbody id="log-body"></tbody></table></div></div>`;
  
  document.getElementById('main-content').innerHTML = html;
  
  // 科室图表
  const depts = await apiFetch('/departments');
  if (depts && depts.length) {
    const deptCounts = [];
    for (const d of depts) {
      const r = await apiFetch(`/employees?department=${d}&per_page=1`);
      deptCounts.push({dept: d, count: r ? r.total : 0});
    }
    renderDeptChart(deptCounts);
  }
  
  // 操作日志
  const logs = await apiFetch('/operation_logs?limit=10');
  if (logs) {
    document.getElementById('log-body').innerHTML = logs.map(l => `<tr><td>${formatDate(l.created_at)}</td><td>${escHtml(l.real_name)}</td><td>${escHtml(l.action)}</td><td>${escHtml(l.module)}</td><td>${escHtml(l.detail)}</td></tr>`).join('');
  }
}

function renderDeptChart(data) {
  const script = document.createElement('script');
  script.src = 'https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js';
  script.onload = () => {
    new Chart(document.getElementById('deptChart'), {
      type: 'bar',
      data: {
        labels: data.map(d=>d.dept),
        datasets: [{ label:'人数', data: data.map(d=>d.count), backgroundColor:'#1a73e8' }]
      },
      options: { responsive: true, maintainAspectRatio: false, plugins:{legend:{display:false}},
        scales:{y:{beginAtZero:true,ticks:{stepSize:1}},x:{ticks:{autoSkip:false,maxRotation:45}}}
      }
    });
  };
  document.head.appendChild(script);
}

// ============================================================
// 人员信息管理
// ============================================================
let personnelPage = 1;
let personnelKeyword = '';
let personnelDept = '';
let personnelStatus = '';

async function loadPersonnel() {
  let html = `<div class="search-bar">
    <input id="emp-search" placeholder="姓名/工号搜索" value="${personnelKeyword}">
    <select id="emp-dept-filter"><option value="">全部科室</option></select>
    <select id="emp-status-filter"><option value="">全部状态</option><option value="在职">在职</option><option value="离职">离职</option><option value="退休">退休</option></select>
    <button class="btn btn-primary" onclick="searchEmployees()">查询</button>
    <button class="btn btn-success" onclick="showAddEmployee()">+ 新增职工</button>
    <button class="btn" onclick="exportEmployees()">导出</button>
  </div>`;
  
  html += `<div class="card"><div class="table-wrap"><table><thead><tr><th><input type="checkbox" id="emp-select-all" onchange="toggleSelectAll(this)"></th><th>工号</th><th>姓名</th><th>科室</th><th>岗位</th><th>职称</th><th>状态</th><th>入职日期</th><th>操作</th></tr></thead><tbody id="emp-table-body"></tbody></table></div>
    <div class="pagination" id="emp-pagination"></div></div>`;
  
  document.getElementById('main-content').innerHTML = html;
  
  // 加载科室选项
  const depts = await apiFetch('/departments');
  const deptSel = document.getElementById('emp-dept-filter');
  if (depts) depts.forEach(d => { deptSel.innerHTML += `<option value="${d}">${d}</option>`; });
  
  searchEmployees();
}

async function searchEmployees() {
  personnelKeyword = document.getElementById('emp-search')?.value || personnelKeyword;
  personnelDept = document.getElementById('emp-dept-filter')?.value || personnelDept;
  personnelStatus = document.getElementById('emp-status-filter')?.value || personnelStatus;
  personnelPage = 1;
  loadEmployeeList();
}

async function loadEmployeeList() {
  const res = await apiFetch(`/employees?keyword=${personnelKeyword}&department=${personnelDept}&status=${personnelStatus}&page=${personnelPage}&per_page=15`);
  if (!res) return;
  
  document.getElementById('emp-table-body').innerHTML = res.data.map(e => `
    <tr><td><input type="checkbox" class="emp-check" value="${e.id}"></td>
    <td>${escHtml(e.emp_no)}</td><td>${escHtml(e.name)}</td><td>${escHtml(e.current_dept||'')}</td>
    <td>${escHtml(e.current_position||'')}</td><td>${escHtml(e.current_title||'')}</td>
    <td>${statusTag(e.status)}</td><td>${formatDate(e.entry_date)}</td>
    <td><button class="btn btn-sm" onclick="viewEmployee(${e.id})">查看</button>
    <button class="btn btn-sm btn-primary" onclick="editEmployee(${e.id})">编辑</button></td></tr>`).join('');
  
  const total = res.total;
  const pages = Math.ceil(total / res.per_page);
  document.getElementById('emp-pagination').innerHTML = `
    <span class="info">共 ${total} 条</span>
    ${Array.from({length:pages}, (_,i) => `<button class="${i+1===personnelPage?'active':''}" onclick="personnelPage=${i+1};loadEmployeeList()">${i+1}</button>`).join('')}`;
}

let currentEmpId = null;

async function viewEmployee(id) {
  currentEmpId = id;
  const emp = await apiFetch(`/employees/${id}`);
  if (!emp) return;
  
  const html = `<div class="detail-panel">
    <div class="detail-sidebar">
      <div class="detail-avatar">${emp.name ? emp.name[0] : '?'}</div>
      <div class="detail-name">${escHtml(emp.name)}</div>
      <div class="detail-title">${escHtml(emp.current_dept||'')} ${escHtml(emp.current_position||'')}</div>
      <dl class="detail-info">
        <dt>工号</dt><dd>${escHtml(emp.emp_no)}</dd>
        <dt>性别</dt><dd>${escHtml(emp.gender)}</dd>
        <dt>民族</dt><dd>${escHtml(emp.ethnicity)}</dd>
        <dt>政治面貌</dt><dd>${escHtml(emp.political_status)}</dd>
        <dt>出生日期</dt><dd>${formatDate(emp.birth_date)}</dd>
        <dt>入职日期</dt><dd>${formatDate(emp.entry_date)}</dd>
        <dt>联系电话</dt><dd>${escHtml(emp.phone_display||emp.phone)}</dd>
        <dt>身份证号</dt><dd>${escHtml(emp.id_card_display||emp.id_card)}</dd>
        <dt>状态</dt><dd>${statusTag(emp.status)}</dd>
      </dl>
    </div>
    <div class="detail-content">
      <div class="tabs">
        <div class="tab active" onclick="showEmpTab('positions',this)">岗位变动</div>
        <div class="tab" onclick="showEmpTab('titles',this)">职称评定</div>
        <div class="tab" onclick="showEmpTab('education',this)">教育经历</div>
        <div class="tab" onclick="showEmpTab('contracts',this)">合同管理</div>
      </div>
      <div id="emp-tab-content"></div>
    </div>
  </div>`;
  
  document.getElementById('main-content').innerHTML = html;
  showEmpTab('positions', document.querySelector('.tab.active'));
}

async function showEmpTab(tab, el) {
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  el.classList.add('active');
  const data = await apiFetch(`/employees/${currentEmpId}`);
  if (!data) return;
  
  const renderers = {
    positions: () => data.positions.map(p => `<tr><td>${escHtml(p.department)}</td><td>${escHtml(p.position)}</td><td>${escHtml(p.job_level)}</td><td>${formatDate(p.start_date)}</td><td>${p.is_current?'<span class="tag tag-success">当前</span>':formatDate(p.end_date)}</td><td>${escHtml(p.change_type)}</td></tr>`).join(''),
    titles: () => data.titles.map(t => `<tr><td>${escHtml(t.title_name)}</td><td><span class="tag ${tagClass(t.title_level)}">${escHtml(t.title_level)}</span></td><td>${escHtml(t.specialty)}</td><td>${formatDate(t.award_date)}</td><td>${t.is_current?'<span class="tag tag-success">当前</span>':''}</td></tr>`).join(''),
    education: () => data.education.map(e => `<tr><td>${escHtml(e.school)}</td><td>${escHtml(e.major)}</td><td>${escHtml(e.degree)}</td><td>${formatDate(e.start_date)} ~ ${formatDate(e.end_date)}</td><td>${e.is_highest?'<span class="tag tag-success">最高</span>':''}</td></tr>`).join(''),
    contracts: () => data.contracts.map(c => `<tr><td>${escHtml(c.contract_no)}</td><td>${escHtml(c.contract_type)}</td><td>${formatDate(c.start_date)} ~ ${formatDate(c.end_date)}</td><td>${statusTag(c.status)}</td></tr>`).join('')
  };
  
  const headers = {
    positions: '<tr><th>科室</th><th>岗位</th><th>级别</th><th>开始</th><th>结束</th><th>类型</th></tr>',
    titles: '<tr><th>职称</th><th>级别</th><th>专业</th><th>评定日期</th><th>状态</th></tr>',
    education: '<tr><th>学校</th><th>专业</th><th>学位</th><th>时间</th><th>标记</th></tr>',
    contracts: '<tr><th>合同号</th><th>类型</th><th>期限</th><th>状态</th></tr>'
  };
  
  document.getElementById('emp-tab-content').innerHTML = `<div class="table-wrap"><table><thead>${headers[tab]}</thead><tbody>${renderers[tab]()}</tbody></table></div>`;
}

async function showAddEmployee() {
  showModal('新增职工', `
    <div class="form-row">
      <div class="form-group"><label>工号</label><input id="add-emp_no" placeholder="DL009"></div>
      <div class="form-group"><label>姓名</label><input id="add-name" placeholder="张三"></div>
      <div class="form-group"><label>性别</label><select id="add-gender"><option>男</option><option>女</option></select></div>
      <div class="form-group"><label>出生日期</label><input id="add-birth_date" type="date"></div>
    </div>
    <div class="form-row">
      <div class="form-group"><label>民族</label><input id="add-ethnicity" value="汉"></div>
      <div class="form-group"><label>政治面貌</label><select id="add-political_status"><option>群众</option><option>共青团员</option><option>中共党员</option></select></div>
      <div class="form-group"><label>婚姻状况</label><select id="add-marital_status"><option>未婚</option><option>已婚</option></select></div>
      <div class="form-group"><label>籍贯</label><input id="add-native_place" value="云南大理"></div>
    </div>
    <div class="form-row">
      <div class="form-group"><label>身份证号</label><input id="add-id_card" placeholder="532901..."></div>
      <div class="form-group"><label>联系电话</label><input id="add-phone" placeholder="138..."></div>
      <div class="form-group"><label>邮箱</label><input id="add-email" placeholder="name@dali-hospital.cn"></div>
      <div class="form-group"><label>入职日期</label><input id="add-entry_date" type="date"></div>
    </div>
    <div class="form-actions"><button class="btn btn-primary" onclick="saveEmployee()">保存</button><button class="btn" onclick="hideModal()">取消</button></div>
  `, 640);
}

async function saveEmployee() {
  const fields = ['emp_no','name','gender','birth_date','ethnicity','political_status','marital_status','native_place','id_card','phone','email','entry_date'];
  const data = {};
  fields.forEach(f => { data[f] = document.getElementById('add-'+f)?.value || ''; });
  if (!data.emp_no || !data.name) { alert('工号和姓名必填'); return; }
  const res = await apiFetch('/employees', {method:'POST', body:JSON.stringify(data)});
  if (res && res.ok) { hideModal(); searchEmployees(); }
  else { alert(res?.error || '保存失败'); }
}

async function editEmployee(id) {
  const emp = await apiFetch(`/employees/${id}`);
  if (!emp) return;
  const fields = ['name','gender','ethnicity','political_status','marital_status','native_place','email','status'];
  const inputs = fields.map(f => `<div class="form-group"><label>${f}</label><input id="edit-${f}" value="${escHtml(emp[f]||'')}"></div>`).join('');
  showModal('编辑职工', `<div class="form-row">${inputs}</div>
    <div class="form-actions"><button class="btn btn-primary" onclick="updateEmployee(${id})">更新</button><button class="btn" onclick="hideModal()">取消</button></div>`);
}

async function updateEmployee(id) {
  const data = {};
  ['name','gender','ethnicity','political_status','marital_status','native_place','email','status'].forEach(f => { data[f] = document.getElementById('edit-'+f)?.value || ''; });
  const res = await apiFetch(`/employees/${id}`, {method:'PUT', body:JSON.stringify(data)});
  if (res && res.ok) { hideModal(); searchEmployees(); }
  else alert(res?.error || '更新失败');
}

function toggleSelectAll(el) {
  document.querySelectorAll('.emp-check').forEach(c => c.checked = el.checked);
}

function exportEmployees() {
  alert('导出功能：将当前筛选结果导出为 Excel 文件（开发中）');
}

// ============================================================
// 工资核算
// ============================================================
let salaryMonth = new Date().toISOString().slice(0,7); // YYYY-MM

async function loadSalary() {
  let html = `<div class="tabs">
    <div class="tab active" onclick="showSalaryTab('calculate',this)">工资核算</div>
    <div class="tab" onclick="showSalaryTab('records',this)">工资记录</div>
    <div class="tab" onclick="showSalaryTab('config',this)">薪资配置</div>
    <div class="tab" onclick="showSalaryTab('stats',this)">统计报表</div>
  </div><div id="salary-tab-content"></div>`;
  
  document.getElementById('main-content').innerHTML = html;
  showSalaryTab('calculate', document.querySelector('.tab.active'));
}

async function showSalaryTab(tab, el) {
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  el.classList.add('active');
  
  const renderers = { calculate: renderSalaryCalculate, records: renderSalaryRecords, config: renderSalaryConfig, stats: renderSalaryStats };
  (renderers[tab] || renderSalaryCalculate)();
}

async function renderSalaryCalculate() {
  let html = `<div class="search-bar">
    <label>核算月份：</label><input id="salary-month" type="month" value="${salaryMonth}">
    <button class="btn btn-primary" onclick="calculateSalary()">计算工资</button>
    <button class="btn btn-success" onclick="approveSalary()">批量审核</button>
  </div>`;
  
  html += `<div class="card"><div class="card-header"><h3>工资核算结果</h3><span class="tag tag-warning">待计算</span></div>
    <div class="table-wrap"><table><thead><tr><th><input type="checkbox" id="salary-select-all" onchange="toggleSelectAll(this)"></th><th>工号</th><th>姓名</th><th>科室</th><th>职称</th><th>应发</th><th>社保</th><th>个税</th><th>实发</th><th>状态</th></tr></thead>
    <tbody id="salary-calc-body"><tr><td colspan="10" style="text-align:center;color:#5f5e5a">请选择月份并点击"计算工资"</td></tr></tbody></table></div></div>`;
  
  document.getElementById('salary-tab-content').innerHTML = html;
}

async function calculateSalary() {
  salaryMonth = document.getElementById('salary-month').value;
  if (!salaryMonth) { alert('请选择月份'); return; }
  const res = await apiFetch('/salary/calculate', {method:'POST', body:JSON.stringify({month: salaryMonth})});
  if (!res) return;
  
  document.getElementById('salary-calc-body').innerHTML = res.data.map(d => `
    <tr><td><input type="checkbox" class="emp-check" value="${d.emp_no}"></td>
    <td>${escHtml(d.emp_no)}</td><td>${escHtml(d.name)}</td><td>${escHtml(d.dept)}</td>
    <td><span class="tag ${tagClass(d.title)}">${escHtml(d.title)}</span></td>
    <td>${fmtMoney(d.gross)}</td><td>${fmtMoney(d.social)}</td><td>${fmtMoney(d.tax)}</td>
    <td><strong>${fmtMoney(d.net)}</strong></td><td>${statusTag('待审核')}</td></tr>`).join('');
  
  // 更新统计
  document.querySelector('.salary-calc .card-header span')?.remove();
}

async function approveSalary() {
  salaryMonth = document.getElementById('salary-month').value;
  if (!salaryMonth) return;
  const res = await apiFetch('/salary/approve', {method:'POST', body:JSON.stringify({month: salaryMonth})});
  if (res && res.ok) { alert('审核完成'); showSalaryTab('records', document.querySelectorAll('.tab')[1]); }
}

async function renderSalaryRecords() {
  let html = `<div class="search-bar">
    <input id="salary-record-month" type="month" value="${salaryMonth}">
    <select id="salary-record-dept"><option value="">全部科室</option></select>
    <button class="btn btn-primary" onclick="loadSalaryRecords()">查询</button>
  </div>`;
  
  html += `<div class="card"><div class="table-wrap"><table><thead><tr><th>工号</th><th>姓名</th><th>科室</th><th>应发合计</th><th>社保扣缴</th><th>个税</th><th>实发工资</th><th>状态</th><th>操作</th></tr></thead><tbody id="salary-records-body"></tbody></table></div></div>`;
  
  document.getElementById('salary-tab-content').innerHTML = html;
  const depts = await apiFetch('/departments');
  const sel = document.getElementById('salary-record-dept');
  if (depts) depts.forEach(d => sel.innerHTML += `<option value="${d}">${d}</option>`);
  
  loadSalaryRecords();
}

async function loadSalaryRecords() {
  salaryMonth = document.getElementById('salary-record-month')?.value || salaryMonth;
  const dept = document.getElementById('salary-record-dept')?.value || '';
  const res = await apiFetch(`/salary/records?month=${salaryMonth}&department=${dept}`);
  if (!res) return;
  document.getElementById('salary-records-body').innerHTML = res.map(r => `
    <tr><td>${escHtml(r.emp_no)}</td><td>${escHtml(r.name)}</td><td>${escHtml(r.dept)}</td>
    <td>${fmtMoney(r.gross_salary)}</td><td>${fmtMoney(r.total_deduction_social)}</td><td>${fmtMoney(r.tax_deduction)}</td>
    <td><strong>${fmtMoney(r.net_salary)}</strong></td><td>${statusTag(r.status)}</td>
    <td><button class="btn btn-sm" onclick="viewSalarySlip(${r.emp_id},'${r.month}')">工资条</button></td></tr>`).join('');
}

async function viewSalarySlip(empId, month) {
  const records = await apiFetch(`/salary/records?month=${month}&emp_id=${empId}`);
  // Actually fetch single record through salary records
  const res = await apiFetch(`/employees/${empId}`);
  if (!res || !records || !records.length) return;
  const s = records[0];
  const e = res;
  
  const html = `<div class="salary-slip">
    <h2>大理大学第一附属医院工资条</h2>
    <div class="period">${month}</div>
    <table>
      <tr class="section-title"><td colspan="2">基本信息</td></tr>
      <tr><td>姓名：${escHtml(e.name)}</td><td>工号：${escHtml(e.emp_no)}</td></tr>
      <tr><td>科室：${escHtml(e.current_dept||'')}</td><td>职称：${escHtml(e.current_title||'')}</td></tr>
      <tr class="section-title"><td colspan="2">收入项目</td></tr>
      <tr><td>基本工资</td><td style="text-align:right">${fmtMoney(s.base_salary)}</td></tr>
      <tr><td>岗位津贴</td><td style="text-align:right">${fmtMoney(s.position_allowance)}</td></tr>
      <tr><td>医疗津贴</td><td style="text-align:right">${fmtMoney(s.medical_allowance)}</td></tr>
      <tr><td>住房补贴</td><td style="text-align:right">${fmtMoney(s.housing_allowance)}</td></tr>
      <tr><td>夜班费</td><td style="text-align:right">${fmtMoney(s.night_shift_pay)}</td></tr>
      <tr><td>加班费</td><td style="text-align:right">${fmtMoney(s.overtime_pay)}</td></tr>
      <tr class="total-row"><td>应发合计</td><td style="text-align:right;font-weight:500">${fmtMoney(s.gross_salary)}</td></tr>
      <tr class="section-title"><td colspan="2">扣缴项目</td></tr>
      <tr><td>养老保险（个人）</td><td style="text-align:right">${fmtMoney(s.pension_personal)}</td></tr>
      <tr><td>医疗保险（个人）</td><td style="text-align:right">${fmtMoney(s.medical_personal)}</td></tr>
      <tr><td>失业保险（个人）</td><td style="text-align:right">${fmtMoney(s.unemployment_personal)}</td></tr>
      <tr><td>住房公积金（个人）</td><td style="text-align:right">${fmtMoney(s.housing_fund_personal)}</td></tr>
      <tr><td>个人所得税</td><td style="text-align:right">${fmtMoney(s.tax_deduction)}</td></tr>
      <tr class="total-row"><td>实发工资</td><td style="text-align:right;font-weight:500;color:#0f6e56">${fmtMoney(s.net_salary)}</td></tr>
    </table>
  </div>`;
  
  showModal('工资条', html, 520);
}

async function renderSalaryConfig() {
  const configs = await apiFetch('/salary/config');
  const si = await apiFetch('/salary/social_insurance');
  const tax = await apiFetch('/salary/tax');
  
  let html = `<div class="card"><div class="card-header"><h3>科室/职称薪资标准</h3><button class="btn btn-sm btn-primary" onclick="showAddSalaryConfig()">+ 新增标准</button></div>
    <div class="table-wrap"><table><thead><tr><th>科室</th><th>职称级别</th><th>基本工资</th><th>岗位津贴</th><th>医疗津贴</th><th>住房补贴</th><th>夜班补贴</th><th>加班倍率</th></tr></thead><tbody>`;
  
  if (configs) configs.forEach(c => {
    html += `<tr><td>${escHtml(c.department)}</td><td><span class="tag ${tagClass(c.title_level)}">${escHtml(c.title_level)}</span></td>
    <td>${fmtMoney(c.base_salary)}</td><td>${fmtMoney(c.position_allowance)}</td><td>${fmtMoney(c.medical_allowance)}</td>
    <td>${fmtMoney(c.housing_allowance)}</td><td>${fmtMoney(c.night_shift_allowance)}</td><td>${c.overtime_rate}x</td></tr>`;
  });
  html += `</tbody></table></div></div>`;
  
  // 社保公积金
  html += `<div class="card"><div class="card-header"><h3>社保公积金缴纳标准（云南省/大理）</h3></div>`;
  if (si) {
    html += `<div class="form-row" style="grid-template-columns:1fr 1fr">
      <div class="metric"><div class="label">养老保险（个人/单位）</div><div class="value">${si.pension_personal_rate}% / ${si.pension_unit_rate}%</div></div>
      <div class="metric"><div class="label">医疗保险（个人/单位）</div><div class="value">${si.medical_personal_rate}% / ${si.medical_unit_rate}%</div></div>
      <div class="metric"><div class="label">失业保险</div><div class="value">${si.unemployment_rate}%</div></div>
      <div class="metric"><div class="label">住房公积金（个人/单位）</div><div class="value">${si.housing_fund_personal_rate}% / ${si.housing_fund_unit_rate}%</div></div>
    </div>`;
  }
  html += `</div>`;
  
  // 个税
  html += `<div class="card"><div class="card-header"><h3>个人所得税税率表（年度累计）</h3></div>
    <div class="table-wrap"><table><thead><tr><th>级数</th><th>累计预扣预缴应纳税所得额</th><th>税率</th><th>速算扣除数</th></tr></thead><tbody>`;
  if (tax) tax.forEach(t => {
    html += `<tr><td>${t.sort_order}</td><td>${fmt(t.bracket_min)} ~ ${t.bracket_max ? fmt(t.bracket_max) : '以上'}</td><td>${t.rate}%</td><td>${fmtMoney(t.deduction)}</td></tr>`;
  });
  html += `</tbody></table></div></div>`;
  
  document.getElementById('salary-tab-content').innerHTML = html;
}

function showAddSalaryConfig() {
  showModal('新增薪资标准', `<div class="form-row">
    <div class="form-group"><label>科室</label><input id="sc-dept"></div>
    <div class="form-group"><label>职称级别</label><select id="sc-title"><option>正高</option><option>副高</option><option>中级</option><option>初级</option></select></div>
    <div class="form-group"><label>基本工资</label><input id="sc-base" type="number"></div>
    <div class="form-group"><label>岗位津贴</label><input id="sc-pos" type="number" value="0"></div>
    <div class="form-group"><label>医疗津贴</label><input id="sc-med" type="number" value="0"></div>
    <div class="form-group"><label>住房补贴</label><input id="sc-house" type="number" value="0"></div>
    <div class="form-group"><label>夜班补贴</label><input id="sc-night" type="number" value="0"></div>
    <div class="form-group"><label>加班倍率</label><input id="sc-ovt" type="number" value="1.5"></div>
  </div>
  <div class="form-actions"><button class="btn btn-primary" onclick="saveSalaryConfig()">保存</button><button class="btn" onclick="hideModal()">取消</button></div>`);
}

async function saveSalaryConfig() {
  const data = {
    department: document.getElementById('sc-dept').value,
    title_level: document.getElementById('sc-title').value,
    base_salary: +document.getElementById('sc-base').value,
    position_allowance: +document.getElementById('sc-pos').value,
    medical_allowance: +document.getElementById('sc-med').value,
    housing_allowance: +document.getElementById('sc-house').value,
    night_shift_allowance: +document.getElementById('sc-night').value,
    overtime_rate: +document.getElementById('sc-ovt').value,
  };
  const res = await apiFetch('/salary/config', {method:'POST', body:JSON.stringify(data)});
  if (res && res.ok) { hideModal(); showSalaryTab('config', document.querySelectorAll('.tab')[2]); }
  else alert(res?.error || '保存失败');
}

async function renderSalaryStats() {
  const res = await apiFetch(`/salary/stats?month=${salaryMonth}`);
  if (!res || res.error) {
    document.getElementById('salary-tab-content').innerHTML = `<div class="card"><p>暂无工资数据，请先核算</p></div>`;
    return;
  }
  const s = res.summary;
  let html = `<div class="metrics">
    <div class="metric"><div class="label">核算人数</div><div class="value primary">${s.emp_count}</div></div>
    <div class="metric"><div class="label">应发总额</div><div class="value">${fmtMoney(s.total_gross)}</div></div>
    <div class="metric"><div class="label">实发总额</div><div class="value success">${fmtMoney(s.total_net)}</div></div>
    <div class="metric"><div class="label">人均实发</div><div class="value">${fmtMoney(s.avg_net)}</div></div>
    <div class="metric"><div class="label">社保总额</div><div class="value warning">${fmtMoney(s.total_social)}</div></div>
    <div class="metric"><div class="label">个税总额</div><div class="value">${fmtMoney(s.total_tax)}</div></div>
  </div>`;
  
  html += `<div class="card"><div class="card-header"><h3>科室工资分布</h3></div><div class="chart-container"><canvas id="salaryDeptChart" role="img" aria-label="科室工资分布图">Loading...</canvas></div></div>`;
  
  document.getElementById('salary-tab-content').innerHTML = html;
  renderSalaryDeptChart(res.by_dept);
}

function renderSalaryDeptChart(data) {
  const script = document.createElement('script');
  script.src = 'https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js';
  script.onload = () => {
    new Chart(document.getElementById('salaryDeptChart'), {
      type: 'bar',
      data: {
        labels: data.map(d => d.dept || '未知'),
        datasets: [
          { label: '应发', data: data.map(d => d.gross), backgroundColor: '#1a73e8' },
          { label: '实发', data: data.map(d => d.net), backgroundColor: '#0f6e56' }
        ]
      },
      options: { responsive: true, maintainAspectRatio: false, plugins:{legend:{display:true,position:'top'}} }
    });
  };
  document.head.appendChild(script);
}

// ============================================================
// 绩效管理
// ============================================================
async function loadPerformance() {
  let html = `<div class="tabs">
    <div class="tab active" onclick="showPerfTab('overview',this)">绩效概览</div>
    <div class="tab" onclick="showPerfTab('templates',this)">考核模板</div>
    <div class="tab" onclick="showPerfTab('assessments',this)">考核评分</div>
    <div class="tab" onclick="showPerfTab('rules',this)">薪酬联动规则</div>
  </div><div id="perf-tab-content"></div>`;
  
  document.getElementById('main-content').innerHTML = html;
  showPerfTab('overview', document.querySelector('.tab.active'));
}

async function showPerfTab(tab, el) {
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  el.classList.add('active');
  const renderers = { overview: renderPerfOverview, templates: renderPerfTemplates, assessments: renderPerfAssessments, rules: renderPerfRules };
  (renderers[tab] || renderPerfOverview)();
}

async function renderPerfOverview() {
  const res = await apiFetch('/perf/stats');
  if (!res || res.error) {
    document.getElementById('perf-tab-content').innerHTML = `<div class="card"><p>暂无绩效数据</p></div>`;
    return;
  }
  const s = res.summary;
  let html = `<div class="metrics">
    <div class="metric"><div class="label">考核人数</div><div class="value primary">${s.total}</div></div>
    <div class="metric"><div class="label">平均得分</div><div class="value">${fmt(s.avg_score,1)}</div></div>
    <div class="metric"><div class="label">优秀(A)</div><div class="value success">${s.a_count}</div></div>
    <div class="metric"><div class="label">良好(B)</div><div class="value">${s.b_count}</div></div>
    <div class="metric"><div class="label">合格(C)</div><div class="value warning">${s.c_count}</div></div>
    <div class="metric"><div class="label">待改进(D)</div><div class="value danger">${s.d_count}</div></div>
  </div>`;
  
  html += `<div class="card"><div class="card-header"><h3>等级分布</h3></div><div class="chart-container"><canvas id="perfLevelChart" role="img" aria-label="绩效等级分布图">Loading...</canvas></div></div>`;
  
  document.getElementById('perf-tab-content').innerHTML = html;
  
  const script = document.createElement('script');
  script.src = 'https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js';
  script.onload = () => {
    new Chart(document.getElementById('perfLevelChart'), {
      type: 'doughnut',
      data: { labels:['A-优秀','B-良好','C-合格','D-待改进','E-不合格'], datasets:[{ data:[s.a_count,s.b_count,s.c_count,s.d_count,s.e_count], backgroundColor:['#0f6e56','#1a73e8','#ba7517','#a32d2d','#501313'] }] },
      options: { responsive:true, maintainAspectRatio:false, plugins:{legend:{position:'right'}} }
    });
  };
  document.head.appendChild(script);
}

async function renderPerfTemplates() {
  const templates = await apiFetch('/perf/templates');
  let html = `<div class="card"><div class="card-header"><h3>考核模板管理</h3><button class="btn btn-sm btn-primary" onclick="showAddTemplate()">+ 新增模板</button></div>`;
  
  if (templates && templates.length) {
    templates.forEach(t => {
      html += `<div class="card" style="margin-bottom:8px;border-left:3px solid #1a73e8">
        <div style="display:flex;justify-content:space-between;align-items:center">
          <div><strong>${escHtml(t.name)}</strong> <span class="tag tag-primary">${escHtml(t.cycle)}</span> ${t.department ? `<span class="tag">${escHtml(t.department)}</span>` : ''}</div>
          <div><button class="btn btn-sm" onclick="viewTemplate(${t.id})">查看维度</button></div>
        </div>
        <div style="margin-top:8px;font-size:12px;color:#5f5e5a">
          ${t.dimensions.map(d => `${escHtml(d.name)}(${d.weight}%)`).join(' / ')}
        </div>
      </div>`;
    });
  } else {
    html += `<p style="text-align:center;color:#5f5e5a;padding:32px">暂无考核模板</p>`;
  }
  html += `</div>`;
  document.getElementById('perf-tab-content').innerHTML = html;
}

function showAddTemplate() {
  showModal('新增考核模板', `<div class="form-row">
    <div class="form-group"><label>模板名称</label><input id="tpl-name" placeholder="医师月度考核"></div>
    <div class="form-group"><label>适用科室</label><input id="tpl-dept" placeholder="内科"></div>
    <div class="form-group"><label>考核周期</label><select id="tpl-cycle"><option>月度</option><option>季度</option><option>年度</option></select></div>
  </div>
  <div class="form-group"><label>考核维度（名称/权重%）label><textarea id="tpl-dims" rows="4" placeholder="医德医风/20&#10;医疗质量/30&#10;患者满意度/20&#10;科研教学/15&#10;团队协作/15"></textarea></div>
  <div class="form-actions"><button class="btn btn-primary" onclick="saveTemplate()">保存</button><button class="btn" onclick="hideModal()">取消</button></div>`);
}

async function saveTemplate() {
  const name = document.getElementById('tpl-name').value;
  const dept = document.getElementById('tpl-dept').value;
  const cycle = document.getElementById('tpl-cycle').value;
  const dimsText = document.getElementById('tpl-dims').value;
  const dims = dimsText.split('\n').filter(l=>l.trim()).map((l,i) => {
    const parts = l.split('/');
    return { name: parts[0].trim(), weight: +parts[1]||0, sort_order: i };
  });
  
  const res = await apiFetch('/perf/templates', {method:'POST', body:JSON.stringify({name,department:dept,cycle,dimensions:dims})});
  if (res && res.ok) { hideModal(); showPerfTab('templates', document.querySelectorAll('.tab')[1]); }
  else alert(res?.error || '保存失败');
}

async function renderPerfAssessments() {
  const period = new Date().toISOString().slice(0,7);
  let html = `<div class="search-bar">
    <input id="perf-period" type="month" value="${period}">
    <select id="perf-dept"><option value="">全部科室</option></select>
    <button class="btn btn-primary" onclick="loadAssessments()">查询</button>
    <button class="btn btn-success" onclick="showNewAssessment()">+ 发起考核</button>
  </div>`;
  
  html += `<div class="card"><div class="table-wrap"><table><thead><tr><th>工号</th><th>姓名</th><th>科室</th><th>考核模板</th><th>周期</th><th>得分</th><th>等级</th><th>状态</th><th>操作</th></tr></thead><tbody id="perf-assess-body"></tbody></table></div></div>`;
  
  document.getElementById('perf-tab-content').innerHTML = html;
  const depts = await apiFetch('/departments');
  if (depts) depts.forEach(d => document.getElementById('perf-dept').innerHTML += `<option value="${d}">${d}</option>`);
  loadAssessments();
}

async function loadAssessments() {
  const period = document.getElementById('perf-period').value;
  const dept = document.getElementById('perf-dept').value;
  const res = await apiFetch(`/perf/assessments?period=${period}&department=${dept}`);
  if (!res) return;
  document.getElementById('perf-assess-body').innerHTML = res.map(a => `
    <tr><td>${escHtml(a.emp_no)}</td><td>${escHtml(a.name)}</td><td>${escHtml(a.dept)}</td>
    <td>${escHtml(a.template_name)}</td><td>${escHtml(a.period)}</td>
    <td>${a.final_score ? fmt(a.final_score,1) : '--'}</td>
    <td>${a.level ? `<span class="tag ${tagClass(a.level)}">${a.level}</span>` : '--'}</td>
    <td>${statusTag(a.status)}</td>
    <td>${a.status==='待评分' ? `<button class="btn btn-sm btn-primary" onclick="scoreAssessment(${a.id})">评分</button>` : `<button class="btn btn-sm" onclick="viewAssessment(${a.id})">查看</button>`}</td></tr>`).join('');
}

async function showNewAssessment() {
  const emps = await apiFetch('/employees?status=在职&per_page=50');
  const templates = await apiFetch('/perf/templates');
  
  let html = `<div class="form-row">
    <div class="form-group"><label>考核职工</label><select id="assess-emp">${emps?.data?.map(e => `<option value="${e.id}">${e.name}(${e.emp_no})</option>`).join('') || ''}</select></div>
    <div class="form-group"><label>考核模板</label><select id="assess-template">${templates?.map(t => `<option value="${t.id}">${t.name}</option>`).join('') || ''}</select></div>
    <div class="form-group"><label>考核周期</label><input id="assess-period" type="month" value="${new Date().toISOString().slice(0,7)}"></div>
  </div>
  <div class="form-actions"><button class="btn btn-primary" onclick="createAssessment()">发起</button><button class="btn" onclick="hideModal()">取消</button></div>`;
  
  showModal('发起绩效考核', html);
}

async function createAssessment() {
  const data = {
    emp_id: +document.getElementById('assess-emp').value,
    template_id: +document.getElementById('assess-template').value,
    period: document.getElementById('assess-period').value,
  };
  const res = await apiFetch('/perf/assess', {method:'POST', body:JSON.stringify(data)});
  if (res && res.ok) { hideModal(); loadAssessments(); }
  else alert(res?.error || '发起失败');
}

async function scoreAssessment(id) {
  const assessment = await apiFetch(`/perf/assess/${id}`);
  if (!assessment) return;
  
  let html = `<h4>考核评分 - ${escHtml(assessment.period)}</h4>`;
  assessment.scores.forEach(s => {
    html += `<div class="form-group" style="margin-bottom:8px">
      <label>${escHtml(s.name)}（权重 ${s.weight}%，满分 ${s.max_score}）</label>
      <div style="display:flex;gap:8px">
        <input id="score-${s.dimension_id}" type="number" min="0" max="${s.max_score}" value="${s.score}" style="width:80px">
        <input id="comment-${s.dimension_id}" placeholder="评语" style="flex:1">
      </div>
    </div>`;
  });
  html += `<div class="form-actions"><button class="btn btn-primary" onclick="submitScores(${id})">提交评分</button><button class="btn" onclick="hideModal()">取消</button></div>`;
  
  showModal('绩效评分', html);
}

async function submitScores(id) {
  const assessment = await apiFetch(`/perf/assess/${id}`);
  const scores = assessment.scores.map(s => ({
    dimension_id: s.dimension_id,
    score: +document.getElementById('score-'+s.dimension_id).value,
    comment: document.getElementById('comment-'+s.dimension_id)?.value || ''
  }));
  const res = await apiFetch(`/perf/assess/${id}`, {method:'PUT', body:JSON.stringify({scores})});
  if (res && res.ok) { hideModal(); alert(`评分完成！得分：${fmt(res.final_score,1)}，等级：${res.level}`); loadAssessments(); }
  else alert(res?.error || '评分失败');
}

async function renderPerfRules() {
  const rules = await apiFetch('/perf/salary_rules');
  let html = `<div class="card"><div class="card-header"><h3>绩效-薪酬联动规则</h3></div>
    <div class="table-wrap"><table><thead><tr><th>等级</th><th>分数范围</th><th>奖金比例</th><th>薪资调整</th><th>说明</th></tr></thead><tbody>`;
  if (rules) rules.forEach(r => {
    html += `<tr><td><span class="tag ${tagClass(r.level)}">${r.level}</span></td><td>${r.min_score} ~ ${r.max_score}</td>
    <td>${r.bonus_rate}%</td><td>${r.salary_adjust_rate > 0 ? '+' : ''}${r.salary_adjust_rate}%</td><td>${escHtml(r.description)}</td></tr>`;
  });
  html += `</tbody></table></div></div>`;
  document.getElementById('perf-tab-content').innerHTML = html;
}

// ============================================================
// 系统设置
// ============================================================
async function loadSettings() {
  let html = `
    <div class="card">
      <div class="card-header"><h3>自定义字段管理</h3><button class="btn btn-sm btn-primary" onclick="showAddCustomField()">+ 新增字段</button></div>
      <div class="table-wrap"><table><thead><tr><th>字段名称</th><th>字段编码</th><th>类型</th><th>适用科室</th><th>必填</th><th>状态</th><th>操作</th></tr></thead><tbody id="custom-fields-body"></tbody></table></div>
    </div>`;
  
  html += `<div class="card">
      <div class="card-header"><h3>工资项目管理</h3><button class="btn btn-sm btn-primary" onclick="showAddSalaryItem()">+ 新增项目</button></div>
      <div class="table-wrap"><table><thead><tr><th>项目名称</th><th>项目编码</th><th>类型</th><th>计税</th><th>显示</th><th>状态</th><th>操作</th></tr></thead><tbody id="salary-items-body"></tbody></table></div>
    </div>`;
  
  html += `<div class="card">
      <div class="card-header"><h3>绩效管理分类</h3><button class="btn btn-sm btn-primary" onclick="showAddPerfCategory()">+ 新增分类</button></div>
      <div class="table-wrap"><table><thead><tr><th>分类名称</th><th>分类编码</th><th>权重</th><th>指标数</th><th>状态</th><th>操作</th></tr></thead><tbody id="perf-categories-body"></tbody></table></div>
    </div>`;
  
  html += `<div class="card"><div class="card-header"><h3>用户管理</h3><button class="btn btn-sm btn-primary" onclick="showAddUser()">+ 新增用户</button></div>
    <div class="table-wrap"><table><thead><tr><th>用户名</th><th>姓名</th><th>角色</th><th>科室</th><th>最后登录</th><th>状态</th></tr></thead><tbody>`;
  
  // 先加载用户数据
  const users = await apiFetch('/users');
  if (users) {
    users.forEach(u => {
      html += `<tr><td>${escHtml(u.username)}</td><td>${escHtml(u.real_name)}</td>
      <td><span class="tag ${u.role==='admin'?'tag-danger':u.role==='hr_mgr'?'tag-warning':'tag-primary'}">${u.role}</span></td>
      <td>${escHtml(u.department||'')}</td><td>${formatDate(u.last_login)}</td><td>${u.is_active?'<span class="tag tag-success">启用</span>':'<span class="tag tag-danger">禁用</span>'}</td></tr>`;
    });
  }
  html += `</tbody></table></div></div>`;
  
  html += `<div class="card"><div class="card-header"><h3>操作日志</h3></div>
    <div class="table-wrap"><table><thead><tr><th>时间</th><th>用户</th><th>操作</th><th>模块</th><th>详情</th></tr></thead><tbody id="settings-log-body"></tbody></table></div></div>`;
  
  document.getElementById('main-content').innerHTML = html;
  
  // 加载自定义字段
  loadCustomFields();
  
  // 加载工资项目
  loadSalaryItems();
  
  // 加载绩效分类
  loadPerfCategories();
  
  // 用户数据已在前面加载并渲染
  
  const logs = await apiFetch('/operation_logs?limit=20');
  if (logs) {
    document.getElementById('settings-log-body').innerHTML = logs.map(l => 
      `<tr><td>${formatDate(l.created_at)}</td><td>${escHtml(l.real_name)}</td><td>${escHtml(l.action)}</td><td>${escHtml(l.module)}</td><td>${escHtml(l.detail)}</td></tr>`).join('');
  }
}

function showAddUser() {
  showModal('新增用户', `<div class="form-row">
    <div class="form-group"><label>用户名</label><input id="new-user-name"></div>
    <div class="form-group"><label>姓名</label><input id="new-real-name"></div>
    <div class="form-group"><label>角色</label><select id="new-role"><option value="staff">普通职工</option><option value="dept_mgr">科室主管</option><option value="hr_mgr">人事主管</option><option value="admin">系统管理员</option></select></div>
    <div class="form-group"><label>初始密码</label><input id="new-password" value="123456"></div>
  </div>
  <div class="form-actions"><button class="btn btn-primary" onclick="saveNewUser()">保存</button><button class="btn" onclick="hideModal()">取消</button></div>`);
}

async function saveNewUser() {
  const data = {
    username: document.getElementById('new-user-name').value,
    real_name: document.getElementById('new-real-name').value,
    role: document.getElementById('new-role').value,
    password: document.getElementById('new-password').value,
  };
  const res = await apiFetch('/users', {method:'POST', body:JSON.stringify(data)});
  if (res && res.ok) { hideModal(); loadSettings(); }
  else alert(res?.error || '创建失败');
}

// ============================================================
// 自定义字段管理
// ============================================================
async function loadCustomFields() {
  const fields = await apiFetch('/custom-fields');
  if (!fields) return;
  
  const tbody = document.getElementById('custom-fields-body');
  if (!tbody) return;
  
  tbody.innerHTML = fields.map(f => `
    <tr>
      <td>${escHtml(f.field_name)}</td>
      <td><code>${escHtml(f.field_code)}</code></td>
      <td><span class="tag tag-primary">${f.field_type}</span></td>
      <td>${f.department ? escHtml(f.department) : '<span style="color:#999">全部</span>'}</td>
      <td>${f.is_required ? '<span class="tag tag-danger">必填</span>' : '<span style="color:#999">选填</span>'}</td>
      <td>${f.is_active ? '<span class="tag tag-success">启用</span>' : '<span class="tag tag-warning">禁用</span>'}</td>
      <td>
        <button class="btn btn-sm" onclick="editCustomField(${f.id})">编辑</button>
        <button class="btn btn-sm btn-danger" onclick="deleteCustomField(${f.id})">删除</button>
      </td>
    </tr>
  `).join('');
}

function showAddCustomField() {
  showModal('新增自定义字段', `
    <div class="form-row">
      <div class="form-group"><label>字段名称 *</label><input id="cf-field-name" placeholder="如：专业特长"></div>
      <div class="form-group"><label>字段编码 *</label><input id="cf-field-code" placeholder="如：specialty"></div>
    </div>
    <div class="form-row">
      <div class="form-group"><label>字段类型</label><select id="cf-field-type">
        <option value="text">文本</option>
        <option value="number">数字</option>
        <option value="date">日期</option>
        <option value="select">下拉选择</option>
        <option value="textarea">多行文本</option>
      </select></div>
      <div class="form-group"><label>适用科室</label><input id="cf-department" placeholder="留空表示全部科室"></div>
    </div>
    <div class="form-row">
      <div class="form-group"><label>选项(仅下拉选择)</label><input id="cf-options" placeholder="用逗号分隔，如：内科,外科,儿科"></div>
      <div class="form-group"><label>排序</label><input id="cf-sort-order" type="number" value="0"></div>
    </div>
    <div class="form-row">
      <div class="form-group"><label>是否必填</label><select id="cf-required"><option value="0">否</option><option value="1">是</option></select></div>
      <div class="form-group"><label>状态</label><select id="cf-active"><option value="1">启用</option><option value="0">禁用</option></select></div>
    </div>
    <div class="form-actions"><button class="btn btn-primary" onclick="saveCustomField()">保存</button><button class="btn" onclick="hideModal()">取消</button></div>
  `, 600);
}

async function saveCustomField(id=null) {
  const data = {
    field_name: document.getElementById('cf-field-name').value,
    field_code: document.getElementById('cf-field-code').value,
    field_type: document.getElementById('cf-field-type').value,
    department: document.getElementById('cf-department').value || null,
    is_required: parseInt(document.getElementById('cf-required').value),
    sort_order: parseInt(document.getElementById('cf-sort-order').value),
    is_active: parseInt(document.getElementById('cf-active').value),
  };
  
  // 处理选项
  const optionsStr = document.getElementById('cf-options').value;
  if (optionsStr && data.field_type === 'select') {
    data.options = optionsStr.split(',').map(s => s.trim()).filter(s => s);
  }
  
  const url = id ? `/custom-fields/${id}` : '/custom-fields';
  const method = id ? 'PUT' : 'POST';
  
  const res = await apiFetch(url, {method, body:JSON.stringify(data)});
  if (res && res.ok) {
    hideModal();
    loadCustomFields();
  } else {
    alert(res?.error || '操作失败');
  }
}

async function editCustomField(id) {
  const fields = await apiFetch('/custom-fields');
  const field = fields.find(f => f.id === id);
  if (!field) return;
  
  showModal('编辑自定义字段', `
    <div class="form-row">
      <div class="form-group"><label>字段名称 *</label><input id="cf-field-name" value="${escHtml(field.field_name)}"></div>
      <div class="form-group"><label>字段编码 *</label><input id="cf-field-code" value="${escHtml(field.field_code)}" ${field.field_code.match(/^builtin_/) ? 'disabled' : ''}></div>
    </div>
    <div class="form-row">
      <div class="form-group"><label>字段类型</label><select id="cf-field-type">
        <option value="text" ${field.field_type==='text'?'selected':''}>文本</option>
        <option value="number" ${field.field_type==='number'?'selected':''}>数字</option>
        <option value="date" ${field.field_type==='date'?'selected':''}>日期</option>
        <option value="select" ${field.field_type==='select'?'selected':''}>下拉选择</option>
        <option value="textarea" ${field.field_type==='textarea'?'selected':''}>多行文本</option>
      </select></div>
      <div class="form-group"><label>适用科室</label><input id="cf-department" value="${escHtml(field.department||'')}"></div>
    </div>
    <div class="form-row">
      <div class="form-group"><label>选项(仅下拉选择)</label><input id="cf-options" value="${Array.isArray(field.options)?field.options.join(','):(field.options||'')}"></div>
      <div class="form-group"><label>排序</label><input id="cf-sort-order" type="number" value="${field.sort_order||0}"></div>
    </div>
    <div class="form-row">
      <div class="form-group"><label>是否必填</label><select id="cf-required"><option value="0" ${!field.is_required?'selected':''}>否</option><option value="1" ${field.is_required?'selected':''}>是</option></select></div>
      <div class="form-group"><label>状态</label><select id="cf-active"><option value="1" ${field.is_active?'selected':''}>启用</option><option value="0" ${!field.is_active?'selected':''}>禁用</option></select></div>
    </div>
    <div class="form-actions"><button class="btn btn-primary" onclick="saveCustomField(${id})">保存</button><button class="btn" onclick="hideModal()">取消</button></div>
  `, 600);
}

async function deleteCustomField(id) {
  if (!confirm('确定要删除这个字段吗？')) return;
  const res = await apiFetch(`/custom-fields/${id}`, {method:'DELETE'});
  if (res && res.ok) {
    loadCustomFields();
  } else {
    alert(res?.error || '删除失败');
  }
}

// ============================================================
// 工资项目管理
// ============================================================
async function loadSalaryItems() {
  const items = await apiFetch('/salary-items');
  if (!items) return;
  
  const tbody = document.getElementById('salary-items-body');
  if (!tbody) return;
  
  tbody.innerHTML = items.map(item => `
    <tr>
      <td>${escHtml(item.item_name)}</td>
      <td><code>${escHtml(item.item_code)}</code></td>
      <td><span class="tag tag-primary">${item.item_type}</span></td>
      <td>${item.is_taxable ? '<span class="tag tag-success">是</span>' : '<span style="color:#999">否</span>'}</td>
      <td>${item.is_visible ? '<span class="tag tag-success">是</span>' : '<span style="color:#999">否</span>'}</td>
      <td>${item.is_active ? '<span class="tag tag-success">启用</span>' : '<span class="tag tag-warning">禁用</span>'}</td>
      <td>
        <button class="btn btn-sm" onclick="editSalaryItem(${item.id})">编辑</button>
        <button class="btn btn-sm btn-danger" onclick="deleteSalaryItem(${item.id})">删除</button>
      </td>
    </tr>
  `).join('');
}

function showAddSalaryItem() {
  showModal('新增工资项目', `
    <div class="form-row">
      <div class="form-group"><label>项目名称 *</label><input id="si-item-name" placeholder="如：基本工资"></div>
      <div class="form-group"><label>项目编码 *</label><input id="si-item-code" placeholder="如：base_salary"></div>
    </div>
    <div class="form-row">
      <div class="form-group"><label>项目类型</label><select id="si-item-type">
        <option value="固定项">固定项</option>
        <option value="浮动项">浮动项</option>
        <option value="扣款项">扣款项</option>
      </select></div>
      <div class="form-group"><label>计算方式</label><select id="si-calc-method">
        <option value="固定值">固定值</option>
        <option value="公式">公式</option>
        <option value="百分比">百分比</option>
      </select></div>
    </div>
    <div class="form-row">
      <div class="form-group"><label>计算公式</label><input id="si-formula" placeholder="如：base*1.2"></div>
      <div class="form-group"><label>排序</label><input id="si-sort-order" type="number" value="0"></div>
    </div>
    <div class="form-row">
      <div class="form-group"><label>是否计税</label><select id="si-taxable"><option value="1">是</option><option value="0">否</option></select></div>
      <div class="form-group"><label>是否显示</label><select id="si-visible"><option value="1">是</option><option value="0">否</option></select></div>
    </div>
    <div class="form-row">
      <div class="form-group"><label>状态</label><select id="si-active"><option value="1">启用</option><option value="0">禁用</option></select></div>
      <div class="form-group"><label>描述</label><input id="si-description" placeholder="可选"></div>
    </div>
    <div class="form-actions"><button class="btn btn-primary" onclick="saveSalaryItem()">保存</button><button class="btn" onclick="hideModal()">取消</button></div>
  `, 600);
}

async function saveSalaryItem(id=null) {
  const data = {
    item_name: document.getElementById('si-item-name').value,
    item_code: document.getElementById('si-item-code').value,
    item_type: document.getElementById('si-item-type').value,
    calculation_method: document.getElementById('si-calc-method').value,
    formula: document.getElementById('si-formula').value || null,
    is_taxable: parseInt(document.getElementById('si-taxable').value),
    is_visible: parseInt(document.getElementById('si-visible').value),
    sort_order: parseInt(document.getElementById('si-sort-order').value),
    is_active: parseInt(document.getElementById('si-active').value),
    description: document.getElementById('si-description').value || null,
  };
  
  const url = id ? `/salary-items/${id}` : '/salary-items';
  const method = id ? 'PUT' : 'POST';
  
  const res = await apiFetch(url, {method, body:JSON.stringify(data)});
  if (res && res.ok) {
    hideModal();
    loadSalaryItems();
  } else {
    alert(res?.error || '操作失败');
  }
}

async function editSalaryItem(id) {
  const items = await apiFetch('/salary-items');
  const item = items.find(i => i.id === id);
  if (!item) return;
  
  showModal('编辑工资项目', `
    <div class="form-row">
      <div class="form-group"><label>项目名称 *</label><input id="si-item-name" value="${escHtml(item.item_name)}"></div>
      <div class="form-group"><label>项目编码 *</label><input id="si-item-code" value="${escHtml(item.item_code)}" disabled></div>
    </div>
    <div class="form-row">
      <div class="form-group"><label>项目类型</label><select id="si-item-type">
        <option value="固定项" ${item.item_type==='固定项'?'selected':''}>固定项</option>
        <option value="浮动项" ${item.item_type==='浮动项'?'selected':''}>浮动项</option>
        <option value="扣款项" ${item.item_type==='扣款项'?'selected':''}>扣款项</option>
      </select></div>
      <div class="form-group"><label>计算方式</label><select id="si-calc-method">
        <option value="固定值" ${item.calculation_method==='固定值'?'selected':''}>固定值</option>
        <option value="公式" ${item.calculation_method==='公式'?'selected':''}>公式</option>
        <option value="百分比" ${item.calculation_method==='百分比'?'selected':''}>百分比</option>
      </select></div>
    </div>
    <div class="form-row">
      <div class="form-group"><label>计算公式</label><input id="si-formula" value="${escHtml(item.formula||'')}"></div>
      <div class="form-group"><label>排序</label><input id="si-sort-order" type="number" value="${item.sort_order||0}"></div>
    </div>
    <div class="form-row">
      <div class="form-group"><label>是否计税</label><select id="si-taxable"><option value="1" ${item.is_taxable?'selected':''}>是</option><option value="0" ${!item.is_taxable?'selected':''}>否</option></select></div>
      <div class="form-group"><label>是否显示</label><select id="si-visible"><option value="1" ${item.is_visible?'selected':''}>是</option><option value="0" ${!item.is_visible?'selected':''}>否</option></select></div>
    </div>
    <div class="form-row">
      <div class="form-group"><label>状态</label><select id="si-active"><option value="1" ${item.is_active?'selected':''}>启用</option><option value="0" ${!item.is_active?'selected':''}>禁用</option></select></div>
      <div class="form-group"><label>描述</label><input id="si-description" value="${escHtml(item.description||'')}"></div>
    </div>
    <div class="form-actions"><button class="btn btn-primary" onclick="saveSalaryItem(${id})">保存</button><button class="btn" onclick="hideModal()">取消</button></div>
  `, 600);
}

async function deleteSalaryItem(id) {
  if (!confirm('确定要删除这个项目吗？')) return;
  const res = await apiFetch(`/salary-items/${id}`, {method:'DELETE'});
  if (res && res.ok) {
    loadSalaryItems();
  } else {
    alert(res?.error || '删除失败');
  }
}

// ============================================================
// 绩效管理分类
// ============================================================
async function loadPerfCategories() {
  const categories = await apiFetch('/perf-categories');
  if (!categories) return;
  
  const tbody = document.getElementById('perf-categories-body');
  if (!tbody) return;
  
  tbody.innerHTML = categories.map(cat => `
    <tr>
      <td>${escHtml(cat.category_name)}</td>
      <td><code>${escHtml(cat.category_code)}</code></td>
      <td>${cat.weight ? cat.weight + '%' : '--'}</td>
      <td>${cat.indicators ? cat.indicators.length : 0}</td>
      <td>${cat.is_active ? '<span class="tag tag-success">启用</span>' : '<span class="tag tag-warning">禁用</span>'}</td>
      <td>
        <button class="btn btn-sm" onclick="editPerfCategory(${cat.id})">编辑</button>
        <button class="btn btn-sm" onclick="showAddPerfIndicator(${cat.id})">+ 指标</button>
        <button class="btn btn-sm btn-danger" onclick="deletePerfCategory(${cat.id})">删除</button>
      </td>
    </tr>
  `).join('');
}

function showAddPerfCategory() {
  showModal('新增绩效分类', `
    <div class="form-row">
      <div class="form-group"><label>分类名称 *</label><input id="pc-category-name" placeholder="如：工作业绩"></div>
      <div class="form-group"><label>分类编码 *</label><input id="pc-category-code" placeholder="如：performance"></div>
    </div>
    <div class="form-row">
      <div class="form-group"><label>权重(%)</label><input id="pc-weight" type="number" value="0" min="0" max="100"></div>
      <div class="form-group"><label>排序</label><input id="pc-sort-order" type="number" value="0"></div>
    </div>
    <div class="form-row">
      <div class="form-group"><label>描述</label><textarea id="pc-description" rows="3"></textarea></div>
    </div>
    <div class="form-actions"><button class="btn btn-primary" onclick="savePerfCategory()">保存</button><button class="btn" onclick="hideModal()">取消</button></div>
  `, 500);
}

async function savePerfCategory(id=null) {
  const data = {
    category_name: document.getElementById('pc-category-name').value,
    category_code: document.getElementById('pc-category-code').value,
    weight: parseFloat(document.getElementById('pc-weight').value) || 0,
    sort_order: parseInt(document.getElementById('pc-sort-order').value),
    description: document.getElementById('pc-description').value || null,
    is_active: 1,
  };
  
  const url = id ? `/perf-categories/${id}` : '/perf-categories';
  const method = id ? 'PUT' : 'POST';
  
  const res = await apiFetch(url, {method, body:JSON.stringify(data)});
  if (res && res.ok) {
    hideModal();
    loadPerfCategories();
  } else {
    alert(res?.error || '操作失败');
  }
}

async function editPerfCategory(id) {
  const categories = await apiFetch('/perf-categories');
  const cat = categories.find(c => c.id === id);
  if (!cat) return;
  
  showModal('编辑绩效分类', `
    <div class="form-row">
      <div class="form-group"><label>分类名称 *</label><input id="pc-category-name" value="${escHtml(cat.category_name)}"></div>
      <div class="form-group"><label>分类编码 *</label><input id="pc-category-code" value="${escHtml(cat.category_code)}" disabled></div>
    </div>
    <div class="form-row">
      <div class="form-group"><label>权重(%)</label><input id="pc-weight" type="number" value="${cat.weight||0}" min="0" max="100"></div>
      <div class="form-group"><label>排序</label><input id="pc-sort-order" type="number" value="${cat.sort_order||0}"></div>
    </div>
    <div class="form-row">
      <div class="form-group"><label>描述</label><textarea id="pc-description" rows="3">${escHtml(cat.description||'')}</textarea></div>
    </div>
    <div class="form-actions"><button class="btn btn-primary" onclick="savePerfCategory(${id})">保存</button><button class="btn" onclick="hideModal()">取消</button></div>
  `, 500);
}

async function deletePerfCategory(id) {
  if (!confirm('确定要删除这个分类吗？关联的指标也会被禁用。')) return;
  const res = await apiFetch(`/perf-categories/${id}`, {method:'DELETE'});
  if (res && res.ok) {
    loadPerfCategories();
  } else {
    alert(res?.error || '删除失败');
  }
}

function showAddPerfIndicator(categoryId) {
  showModal('新增绩效指标', `
    <div class="form-row">
      <div class="form-group"><label>指标名称 *</label><input id="pi-indicator-name" placeholder="如：门诊量"></div>
      <div class="form-group"><label>指标编码 *</label><input id="pi-indicator-code" placeholder="如：outpatient_count"></div>
    </div>
    <div class="form-row">
      <div class="form-group"><label>评分方式</label><select id="pi-scoring-method">
        <option value="百分制">百分制</option>
        <option value="等级制">等级制</option>
        <option value="定量">定量</option>
      </select></div>
      <div class="form-group"><label>满分</label><input id="pi-max-score" type="number" value="100"></div>
    </div>
    <div class="form-row">
      <div class="form-group"><label>权重(%)</label><input id="pi-weight" type="number" value="0" min="0" max="100"></div>
      <div class="form-group"><label>排序</label><input id="pi-sort-order" type="number" value="0"></div>
    </div>
    <div class="form-row">
      <div class="form-group"><label>描述</label><textarea id="pi-description" rows="3"></textarea></div>
    </div>
    <div class="form-actions"><button class="btn btn-primary" onclick="savePerfIndicator(${categoryId})">保存</button><button class="btn" onclick="hideModal()">取消</button></div>
  `, 500);
}

async function savePerfIndicator(categoryId) {
  const data = {
    indicator_name: document.getElementById('pi-indicator-name').value,
    indicator_code: document.getElementById('pi-indicator-code').value,
    category_id: categoryId,
    scoring_method: document.getElementById('pi-scoring-method').value,
    max_score: parseFloat(document.getElementById('pi-max-score').value) || 100,
    weight: parseFloat(document.getElementById('pi-weight').value) || 0,
    sort_order: parseInt(document.getElementById('pi-sort-order').value),
    description: document.getElementById('pi-description').value || null,
    is_active: 1,
  };
  
  const res = await apiFetch('/perf-indicators', {method:'POST', body:JSON.stringify(data)});
  if (res && res.ok) {
    hideModal();
    loadPerfCategories();
  } else {
    alert(res?.error || '操作失败');
  }
}

// ============================================================
// 弹窗
// ============================================================
function showModal(title, content, width=500) {
  const overlay = document.getElementById('modal-overlay');
  const modal = document.getElementById('modal-box');
  document.getElementById('modal-title').textContent = title;
  document.getElementById('modal-body').innerHTML = content;
  modal.style.maxWidth = width + 'px';
  overlay.classList.add('show');
}

function hideModal() {
  document.getElementById('modal-overlay').classList.remove('show');
}

// ============================================================
// 初始化
// ============================================================
document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('modal-overlay').addEventListener('click', e => { if (e.target.id === 'modal-overlay') hideModal(); });
  checkSession();
});
