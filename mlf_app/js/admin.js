// Admin Control Panel & Dashboard Controller
(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        define(['MLFAuth'], factory);
    } else if (typeof module === 'object' && module.exports) {
        module.exports = factory(require('./auth'));
    } else {
        root.MLFAdmin = factory(root.MLFAuth);
    }
}(typeof self !== 'undefined' ? self : this, function (Auth) {
    'use strict';

    let questionsData = [];

    const Admin = {
        init: function (questions) {
            questionsData = questions || window.MLF_QUESTIONS || [];
            this.bindEvents();
            this.renderOverview();
            this.renderUsersTable();
            this.renderAttemptsTable();
            this.renderQuestionsTable();
            this.renderSyllabusAnalytics();
        },

        bindEvents: function () {
            // Admin Navigation Tabs
            document.querySelectorAll('.admin-nav-tab').forEach(tab => {
                tab.addEventListener('click', () => {
                    document.querySelectorAll('.admin-nav-tab').forEach(t => t.classList.remove('active'));
                    document.querySelectorAll('.admin-tab-content').forEach(c => c.style.display = 'none');
                    tab.classList.add('active');
                    const targetId = tab.dataset.tab;
                    const contentElem = document.getElementById(targetId);
                    if (contentElem) contentElem.style.display = 'block';

                    // Re-render when active
                    if (targetId === 'adminTabUsers') Admin.renderUsersTable();
                    if (targetId === 'adminTabAttempts') Admin.renderAttemptsTable();
                    if (targetId === 'adminTabQuestions') Admin.renderQuestionsTable();
                    if (targetId === 'adminTabAnalytics') Admin.renderSyllabusAnalytics();
                });
            });

            // User Search & Filter
            const userSearch = document.getElementById('adminUserSearch');
            if (userSearch) {
                userSearch.addEventListener('input', () => Admin.renderUsersTable());
            }
            const roleFilter = document.getElementById('adminUserRoleFilter');
            if (roleFilter) {
                roleFilter.addEventListener('change', () => Admin.renderUsersTable());
            }

            // Question Search & Filter
            const qSearch = document.getElementById('adminQSearch');
            if (qSearch) {
                qSearch.addEventListener('input', () => Admin.renderQuestionsTable());
            }
            const qWeekFilter = document.getElementById('adminQWeekFilter');
            if (qWeekFilter) {
                qWeekFilter.addEventListener('change', () => Admin.renderQuestionsTable());
            }

            // Add User Button & Modal
            const btnOpenAddUser = document.getElementById('btnOpenAddUser');
            const addUserModal = document.getElementById('addUserModal');
            const closeAddUser = document.getElementById('closeAddUserModal');
            const cancelAddUser = document.getElementById('cancelAddUserBtn');
            const formAddUser = document.getElementById('formAddUser');

            if (btnOpenAddUser && addUserModal) {
                btnOpenAddUser.addEventListener('click', () => addUserModal.style.display = 'flex');
            }
            if (closeAddUser && addUserModal) {
                closeAddUser.addEventListener('click', () => addUserModal.style.display = 'none');
            }
            if (cancelAddUser && addUserModal) {
                cancelAddUser.addEventListener('click', () => addUserModal.style.display = 'none');
            }
            if (formAddUser) {
                formAddUser.addEventListener('submit', (e) => {
                    e.preventDefault();
                    const name = document.getElementById('newUserName').value.trim();
                    const email = document.getElementById('newUserEmail').value.trim();
                    const rollNo = document.getElementById('newUserRoll').value.trim();
                    const password = document.getElementById('newUserPassword').value.trim();
                    const role = document.getElementById('newUserRole').value;

                    const res = Auth.signUp(name, email, rollNo, password, role);
                    if (res.success) {
                        alert(`User ${name} successfully registered.`);
                        formAddUser.reset();
                        addUserModal.style.display = 'none';
                        Admin.renderOverview();
                        Admin.renderUsersTable();
                    } else {
                        alert(res.error || 'Failed to add user.');
                    }
                });
            }

            // Export Data Buttons
            const btnExportJson = document.getElementById('btnExportJson');
            if (btnExportJson) {
                btnExportJson.addEventListener('click', () => Admin.exportDataJson());
            }

            const btnExportCsv = document.getElementById('btnExportCsv');
            if (btnExportCsv) {
                btnExportCsv.addEventListener('click', () => Admin.exportAttemptsCsv());
            }

            // Reset Data Button
            const btnResetData = document.getElementById('btnResetSystemData');
            if (btnResetData) {
                btnResetData.addEventListener('click', () => {
                    if (confirm('WARNING: Reset system database to defaults? All test history will be reset.')) {
                        Auth.resetAllData();
                        location.reload();
                    }
                });
            }
        },

        renderOverview: function () {
            const users = Auth.getAllUsers();
            const attempts = Auth.getAllAttempts();

            const totalUsersElem = document.getElementById('kpiTotalUsers');
            const totalAttemptsElem = document.getElementById('kpiTotalAttempts');
            const avgScoreElem = document.getElementById('kpiAvgScore');
            const avgAccElem = document.getElementById('kpiAvgAccuracy');
            const qCountElem = document.getElementById('kpiTotalQuestions');

            if (totalUsersElem) totalUsersElem.textContent = users.length;
            if (totalAttemptsElem) totalAttemptsElem.textContent = attempts.length;
            if (qCountElem) qCountElem.textContent = questionsData.length || 210;

            if (attempts.length > 0) {
                const totalScoreSum = attempts.reduce((acc, a) => acc + (a.score || 0), 0);
                const totalAccSum = attempts.reduce((acc, a) => acc + (a.accuracy || 0), 0);
                if (avgScoreElem) avgScoreElem.textContent = Math.round(totalScoreSum / attempts.length);
                if (avgAccElem) avgAccElem.textContent = Math.round(totalAccSum / attempts.length) + '%';
            } else {
                if (avgScoreElem) avgScoreElem.textContent = '0';
                if (avgAccElem) avgAccElem.textContent = '0%';
            }
        },

        renderUsersTable: function () {
            const tbody = document.getElementById('adminUsersTbody');
            if (!tbody) return;

            const searchVal = (document.getElementById('adminUserSearch')?.value || '').toLowerCase();
            const roleFilter = document.getElementById('adminUserRoleFilter')?.value || 'ALL';

            const users = Auth.getAllUsers().filter(u => {
                const matchSearch = u.name.toLowerCase().includes(searchVal) || 
                                    u.email.toLowerCase().includes(searchVal) || 
                                    u.rollNo.toLowerCase().includes(searchVal);
                const matchRole = roleFilter === 'ALL' || u.role === roleFilter;
                return matchSearch && matchRole;
            });

            tbody.innerHTML = '';
            if (users.length === 0) {
                tbody.innerHTML = '<tr><td colspan="8" style="text-align: center; color: #64748b; padding: 20px;">No users found matching search criteria.</td></tr>';
                return;
            }

            users.forEach(u => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td><strong>${u.name}</strong></td>
                    <td>${u.email}</td>
                    <td><code>${u.rollNo}</code></td>
                    <td><span class="role-badge role-${u.role}">${u.role.toUpperCase()}</span></td>
                    <td>${u.testsTaken || 0}</td>
                    <td><strong>${u.bestScore || 0}</strong></td>
                    <td><span class="status-pill status-${u.status}">${u.status.toUpperCase()}</span></td>
                    <td>
                        ${u.role !== 'admin' ? `
                            <button class="tbl-action-btn btn-toggle" data-uid="${u.id}" title="Toggle Active / Suspended">
                                ${u.status === 'active' ? 'Suspend' : 'Activate'}
                            </button>
                            <button class="tbl-action-btn btn-reset" data-uid="${u.id}" title="Reset Password">Reset</button>
                            <button class="tbl-action-btn btn-del" data-uid="${u.id}" title="Delete User">✕</button>
                        ` : '<span style="color: #64748b; font-size: 11px;">Protected</span>'}
                    </td>
                `;

                // Bind action buttons
                const btnToggle = tr.querySelector('.btn-toggle');
                if (btnToggle) {
                    btnToggle.addEventListener('click', () => {
                        Auth.toggleUserStatus(u.id);
                        Admin.renderUsersTable();
                    });
                }

                const btnReset = tr.querySelector('.btn-reset');
                if (btnReset) {
                    btnReset.addEventListener('click', () => {
                        const newPass = prompt(`Enter new password for ${u.name}:`, 'Student@123');
                        if (newPass) {
                            Auth.resetUserPassword(u.id, newPass);
                            alert(`Password for ${u.name} has been updated.`);
                        }
                    });
                }

                const btnDel = tr.querySelector('.btn-del');
                if (btnDel) {
                    btnDel.addEventListener('click', () => {
                        if (confirm(`Are you sure you want to delete user ${u.name}?`)) {
                            Auth.deleteUser(u.id);
                            Admin.renderOverview();
                            Admin.renderUsersTable();
                        }
                    });
                }

                tbody.appendChild(tr);
            });
        },

        renderAttemptsTable: function () {
            const tbody = document.getElementById('adminAttemptsTbody');
            if (!tbody) return;

            const attempts = Auth.getAllAttempts();
            tbody.innerHTML = '';

            if (attempts.length === 0) {
                tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; color: #64748b; padding: 20px;">No test attempts recorded yet.</td></tr>';
                return;
            }

            attempts.forEach(a => {
                const tr = document.createElement('tr');
                const dateStr = a.timestamp ? new Date(a.timestamp).toLocaleString() : 'N/A';
                tr.innerHTML = `
                    <td><code>${a.id}</code></td>
                    <td><strong>${a.userName}</strong> (${a.userRoll})</td>
                    <td>${a.section}</td>
                    <td>${dateStr}</td>
                    <td><strong style="color: #1e3a8a;">${a.score}</strong> / ${a.maxMarks}</td>
                    <td><span class="acc-pill ${a.accuracy >= 70 ? 'acc-high' : 'acc-low'}">${a.accuracy}%</span></td>
                    <td>${a.timeSpent || 'N/A'}</td>
                `;
                tbody.appendChild(tr);
            });
        },

        renderQuestionsTable: function () {
            const tbody = document.getElementById('adminQuestionsTbody');
            if (!tbody) return;

            const searchVal = (document.getElementById('adminQSearch')?.value || '').toLowerCase();
            const weekVal = document.getElementById('adminQWeekFilter')?.value || 'ALL';

            const filtered = questionsData.filter(q => {
                const matchWeek = (weekVal === 'ALL' || q.week === weekVal);
                const stem = (q.question_text || '').toLowerCase();
                const matchSearch = q.id.toLowerCase().includes(searchVal) || 
                                    stem.includes(searchVal) || 
                                    q.subtopic.toLowerCase().includes(searchVal);
                return matchWeek && matchSearch;
            });

            tbody.innerHTML = '';
            if (filtered.length === 0) {
                tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; color: #64748b; padding: 20px;">No questions match filter.</td></tr>';
                return;
            }

            // Display first 50 matching to maintain ultra-fast rendering
            filtered.slice(0, 50).forEach(q => {
                const tr = document.createElement('tr');
                const stemPreview = q.question_text ? (q.question_text.slice(0, 75) + '...') : '[Diagram/Formula Question]';
                tr.innerHTML = `
                    <td><strong>${q.id}</strong></td>
                    <td><span class="q-type-badge">${q.question_type}</span></td>
                    <td><strong>${q.week}</strong><br/><small style="color: #64748b;">${q.subtopic}</small></td>
                    <td>+${q.marks}</td>
                    <td>${stemPreview}</td>
                    <td><span class="status-pill status-active">ACTIVE</span></td>
                `;
                tbody.appendChild(tr);
            });

            const countIndicator = document.getElementById('adminQCountIndicator');
            if (countIndicator) {
                countIndicator.textContent = `Showing ${Math.min(filtered.length, 50)} of ${filtered.length} matching questions (Total: ${questionsData.length})`;
            }
        },

        renderSyllabusAnalytics: function () {
            const container = document.getElementById('adminSyllabusBarsContainer');
            if (!container) return;

            const weeks = [
                { name: "Week 1 - ML Foundations", count: 95, icon: "🧠" },
                { name: "Week 2 - Mathematical Foundations", count: 22, icon: "📐" },
                { name: "Week 3 - Linear Algebra & Subspaces", count: 63, icon: "🔢" },
                { name: "Week 4 - Regression & Eigenvalues", count: 30, icon: "📊" }
            ];

            container.innerHTML = '';

            weeks.forEach(w => {
                const div = document.createElement('div');
                div.className = 'syllabus-stat-row';
                const pct = Math.round((w.count / 210) * 100);
                div.innerHTML = `
                    <div class="stat-row-header">
                        <span><strong>${w.icon} ${w.name}</strong></span>
                        <span><strong>${w.count} Questions</strong> (${pct}%)</span>
                    </div>
                    <div class="stat-progress-bar">
                        <div class="stat-progress-fill" style="width: ${pct}%;"></div>
                    </div>
                `;
                container.appendChild(div);
            });
        },

        exportDataJson: function () {
            const exportObj = {
                exportedAt: new Date().toISOString(),
                users: Auth.getAllUsers(),
                attempts: Auth.getAllAttempts(),
                totalQuestions: questionsData.length
            };
            const blob = new Blob([JSON.stringify(exportObj, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `mlf_platform_export_${Date.now()}.json`;
            a.click();
            URL.revokeObjectURL(url);
        },

        exportAttemptsCsv: function () {
            const attempts = Auth.getAllAttempts();
            if (attempts.length === 0) {
                alert('No attempts to export.');
                return;
            }

            const headers = ['Attempt ID', 'User Name', 'Roll Number', 'Section', 'Date Time', 'Score', 'Max Marks', 'Accuracy (%)', 'Time Spent'];
            const rows = attempts.map(a => [
                a.id,
                `"${a.userName}"`,
                a.userRoll,
                `"${a.section}"`,
                `"${a.timestamp}"`,
                a.score,
                a.maxMarks,
                a.accuracy,
                `"${a.timeSpent}"`
            ]);

            const csvContent = [headers.join(','), ...rows.map(r => r.join(','))].join('\n');
            const blob = new Blob([csvContent], { type: 'text/csv' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `mlf_test_attempts_${Date.now()}.csv`;
            a.click();
            URL.revokeObjectURL(url);
        }
    };

    return Admin;
}));
