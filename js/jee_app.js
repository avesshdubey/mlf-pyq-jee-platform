// JEE Examination CBT Engine - Machine Learning Foundations (MLF)
(function () {
    'use strict';

    // State Variables
    let allQuestions = [];
    let currentQuestions = [];
    let currentIndex = 0;
    let currentWeekFilter = 'ALL';
    let currentSubtopicFilter = 'ALL';
    
    // User responses: questionId -> { status, selectedOptions, value }
    let responses = {};

    // Timer state
    let totalSeconds = 180 * 60; // 180 minutes
    let timerInterval = null;
    let isPaused = false;
    let isExamSubmitted = false;

    // DOM Elements
    const elements = {
        timerDisplay: document.getElementById('timerDisplay'),
        pauseTimerBtn: document.getElementById('pauseTimerBtn'),
        sectionTabs: document.getElementById('sectionTabs'),
        subtopicSelect: document.getElementById('subtopicFilterSelect'),
        paletteSecLabel: document.getElementById('paletteSecLabel'),
        paletteGrid: document.getElementById('paletteGrid'),
        
        // Header & User elements
        headerUserName: document.getElementById('headerUserName'),
        headerUserRoll: document.getElementById('headerUserRoll'),
        headerUserRole: document.getElementById('headerUserRole'),
        btnToggleAdminView: document.getElementById('btnToggleAdminView'),
        btnToggleExamView: document.getElementById('btnToggleExamView'),
        btnLogout: document.getElementById('btnLogout'),
        
        // Views
        examInterfaceView: document.getElementById('examInterfaceView'),
        adminDashboardView: document.getElementById('adminDashboardView'),
        scorecardView: document.getElementById('scorecardView'),
        examMain: document.getElementById('examMain'),

        // Auth Modal elements
        authModal: document.getElementById('authModal'),
        tabLoginBtn: document.getElementById('tabLoginBtn'),
        tabSignupBtn: document.getElementById('tabSignupBtn'),
        formLogin: document.getElementById('formLogin'),
        formSignup: document.getElementById('formSignup'),
        authAlert: document.getElementById('authAlert'),
        btnQuickStudent: document.getElementById('btnQuickStudent'),
        btnQuickAdmin: document.getElementById('btnQuickAdmin'),

        // Question View
        currentQDisplayNum: document.getElementById('currentQDisplayNum'),
        currentQTypeBadge: document.getElementById('currentQTypeBadge'),
        currentQSubtopic: document.getElementById('currentQSubtopic'),
        markPosDisplay: document.getElementById('markPosDisplay'),
        markNegDisplay: document.getElementById('markNegDisplay'),
        qSourceList: document.getElementById('qSourceList'),
        qStemText: document.getElementById('qStemText'),
        qStemImageBox: document.getElementById('qStemImageBox'),
        qStemImage: document.getElementById('qStemImage'),
        qInputContainer: document.getElementById('qInputContainer'),
        
        // Navigation Buttons
        btnPrevious: document.getElementById('btnPrevious'),
        btnSaveNext: document.getElementById('btnSaveNext'),
        btnClearResponse: document.getElementById('btnClearResponse'),
        btnMarkReviewNext: document.getElementById('btnMarkReviewNext'),
        btnSubmitTest: document.getElementById('btnSubmitTest'),

        // Counters in Legend
        countAnswered: document.getElementById('countAnswered'),
        countNotAnswered: document.getElementById('countNotAnswered'),
        countNotVisited: document.getElementById('countNotVisited'),
        countMarked: document.getElementById('countMarked'),
        countMarkedAnswered: document.getElementById('countMarkedAnswered'),

        // Modals
        qpModal: document.getElementById('qpModal'),
        qpModalContent: document.getElementById('qpModalContent'),
        viewQPBtn: document.getElementById('viewQPBtn'),
        closeQpModal: document.getElementById('closeQpModal'),
        closeQpModalBtn: document.getElementById('closeQpModalBtn'),

        instModal: document.getElementById('instModal'),
        viewInstBtn: document.getElementById('viewInstBtn'),
        closeInstModal: document.getElementById('closeInstModal'),
        closeInstModalBtn: document.getElementById('closeInstModalBtn'),

        submitModal: document.getElementById('submitModal'),
        submitSummaryTbody: document.getElementById('submitSummaryTbody'),
        cancelSubmitBtn: document.getElementById('cancelSubmitBtn'),
        confirmSubmitBtn: document.getElementById('confirmSubmitBtn'),
        closeSubmitModal: document.getElementById('closeSubmitModal'),

        // Scorecard View
        resTotalScore: document.getElementById('resTotalScore'),
        resMaxMarks: document.getElementById('resMaxMarks'),
        resAccuracy: document.getElementById('resAccuracy'),
        resAttempted: document.getElementById('resAttempted'),
        categoryPerfTbody: document.getElementById('categoryPerfTbody'),
        reviewQuestionsList: document.getElementById('reviewQuestionsList'),
        btnRestartTest: document.getElementById('btnRestartTest')
    };

    // Initialize Application
    function init() {
        if (window.MLF_QUESTIONS && Array.isArray(window.MLF_QUESTIONS)) {
            loadQuestions(window.MLF_QUESTIONS);
        } else {
            fetch('data/questions.json')
                .then(r => r.json())
                .then(data => loadQuestions(data))
                .catch(err => {
                    console.error("Failed to load questions:", err);
                    elements.qStemText.textContent = "Error loading question bank. Please check questions.json.";
                });
        }
    }

    function loadQuestions(data) {
        allQuestions = data;
        
        // Initialize responses
        allQuestions.forEach(q => {
            responses[q.id] = {
                status: 'NOT_VISITED',
                selectedOptions: [], // For MCQ / MSQ
                value: ''            // For SA / Numerical
            };
        });

        // Set first question as NOT_ANSWERED upon visit
        if (allQuestions.length > 0) {
            responses[allQuestions[0].id].status = 'NOT_ANSWERED';
        }

        // Dynamically compute and display week counts and total questions
        const weekCounts = {
            'ALL': allQuestions.length,
            'Week 1 - ML Foundations': 0,
            'Week 2 - Mathematical Foundations': 0,
            'Week 3 - Linear Algebra & Subspaces': 0,
            'Week 4 - Regression & Eigenvalues': 0
        };
        allQuestions.forEach(q => {
            if (weekCounts[q.week] !== undefined) weekCounts[q.week]++;
        });
        elements.sectionTabs.querySelectorAll('.sec-tab').forEach(tab => {
            const wk = tab.dataset.week;
            if (wk === 'ALL') tab.textContent = `All Weeks (${weekCounts['ALL']})`;
            else if (wk === 'Week 1 - ML Foundations') tab.textContent = `Week 1: ML Foundations (${weekCounts[wk]})`;
            else if (wk === 'Week 2 - Mathematical Foundations') tab.textContent = `Week 2: Math Foundations (${weekCounts[wk]})`;
            else if (wk === 'Week 3 - Linear Algebra & Subspaces') tab.textContent = `Week 3: Linear Algebra (${weekCounts[wk]})`;
            else if (wk === 'Week 4 - Regression & Eigenvalues') tab.textContent = `Week 4: Regression & Eigen (${weekCounts[wk]})`;
        });
        elements.countNotVisited.textContent = allQuestions.length;

        buildSubtopicDropdown();
        applyFilter();
        bindEvents();

        // Check authentication & initialize UI/timer
        checkAuthAndSetupUI();
    }

    // ==================== AUTHENTICATION & ROLE GUARDS ====================
    function checkAuthAndSetupUI() {
        if (!window.MLFAuth) return;

        const curUser = window.MLFAuth.getCurrentUser();

        if (curUser) {
            // User is signed in
            elements.authModal.style.display = 'none';
            elements.headerUserName.textContent = curUser.name;
            elements.headerUserRoll.textContent = curUser.rollNo;
            elements.headerUserRole.textContent = curUser.role.toUpperCase();

            if (curUser.role === 'admin') {
                elements.btnToggleAdminView.style.display = 'inline-block';
                // Initialize Admin Controller
                if (window.MLFAdmin) {
                    window.MLFAdmin.init(allQuestions);
                }
            } else {
                elements.btnToggleAdminView.style.display = 'none';
                elements.btnToggleExamView.style.display = 'none';
                if (!isExamSubmitted) {
                    elements.examInterfaceView.style.display = 'block';
                    elements.scorecardView.style.display = 'none';
                }
                elements.adminDashboardView.style.display = 'none';
            }

            // Start timer only if exam is in progress
            if (!isExamSubmitted && elements.examInterfaceView.style.display !== 'none') {
                startTimer();
            }
        } else {
            // User is NOT signed in: trigger auth modal and stop timer
            stopTimer();
            elements.authModal.style.display = 'flex';
            elements.btnToggleAdminView.style.display = 'none';
            elements.btnToggleExamView.style.display = 'none';
        }
    }

    function resetExamState() {
        isExamSubmitted = false;
        stopTimer();
        responses = {};
        allQuestions.forEach(q => {
            responses[q.id] = {
                status: 'NOT_VISITED',
                selectedOptions: [],
                value: ''
            };
        });
        currentIndex = 0;
        totalSeconds = 180 * 60;
        isPaused = false;
        updateTimerDisplay();
        elements.countNotVisited.textContent = allQuestions.length;
        applyFilter();
    }

    function showAuthAlert(msg, isSuccess = false) {
        elements.authAlert.textContent = msg;
        elements.authAlert.className = `auth-alert ${isSuccess ? 'success' : 'error'}`;
        elements.authAlert.style.display = 'block';
    }

    function hideAuthAlert() {
        elements.authAlert.style.display = 'none';
    }

    function buildSubtopicDropdown() {
        const subtopics = new Set();
        allQuestions.forEach(q => {
            if (currentWeekFilter === 'ALL' || q.week === currentWeekFilter) {
                if (q.subtopic) subtopics.add(q.subtopic);
            }
        });

        elements.subtopicSelect.innerHTML = '<option value="ALL">All Subtopics</option>';
        Array.from(subtopics).sort().forEach(st => {
            const opt = document.createElement('option');
            opt.value = st;
            opt.textContent = st;
            elements.subtopicSelect.appendChild(opt);
        });
    }

    function applyFilter() {
        currentQuestions = allQuestions.filter(q => {
            const matchWeek = (currentWeekFilter === 'ALL' || q.week === currentWeekFilter);
            const matchSub = (currentSubtopicFilter === 'ALL' || q.subtopic === currentSubtopicFilter);
            return matchWeek && matchSub;
        });

        currentIndex = 0;
        if (currentQuestions.length > 0) {
            const curQ = currentQuestions[0];
            if (responses[curQ.id].status === 'NOT_VISITED') {
                responses[curQ.id].status = 'NOT_ANSWERED';
            }
        }

        updatePaletteSecLabel();
        renderPalette();
        renderCurrentQuestion();
        updateLegendCounters();
    }

    function updatePaletteSecLabel() {
        let label = currentWeekFilter === 'ALL' ? 'All Questions' : currentWeekFilter;
        if (currentSubtopicFilter !== 'ALL') {
            label += ` (${currentSubtopicFilter})`;
        }
        elements.paletteSecLabel.textContent = `${label} [${currentQuestions.length}]`;
    }

    function startTimer() {
        if (timerInterval) clearInterval(timerInterval);
        timerInterval = setInterval(() => {
            const curUser = window.MLFAuth ? window.MLFAuth.getCurrentUser() : null;
            const isExamActive = curUser && elements.examInterfaceView && elements.examInterfaceView.style.display !== 'none' && !isExamSubmitted;
            
            if (!isExamActive) {
                return;
            }

            if (!isPaused && totalSeconds > 0) {
                totalSeconds--;
                updateTimerDisplay();
            } else if (totalSeconds <= 0) {
                clearInterval(timerInterval);
                timerInterval = null;
                alert("Time's up! Submitting examination automatically.");
                submitExam();
            }
        }, 1000);
    }

    function stopTimer() {
        if (timerInterval) {
            clearInterval(timerInterval);
            timerInterval = null;
        }
    }

    function updateTimerDisplay() {
        const hours = Math.floor(totalSeconds / 3600);
        const minutes = Math.floor((totalSeconds % 3600) / 60);
        const seconds = totalSeconds % 60;
        
        const pad = (n) => String(n).padStart(2, '0');
        if (hours > 0) {
            elements.timerDisplay.textContent = `${pad(hours)}:${pad(minutes)}:${pad(seconds)}`;
        } else {
            elements.timerDisplay.textContent = `${pad(minutes)}:${pad(seconds)}`;
        }

        if (totalSeconds < 600) { // Under 10 mins
            elements.timerDisplay.style.color = '#dc2626';
        }
    }

    // Render Current Question
    function renderCurrentQuestion() {
        if (currentQuestions.length === 0) {
            elements.qStemText.textContent = "No questions found matching current filter.";
            elements.qInputContainer.innerHTML = '';
            elements.qStemImageBox.style.display = 'none';
            return;
        }

        const q = currentQuestions[currentIndex];
        const resp = responses[q.id];

        // Transition from NOT_VISITED to NOT_ANSWERED
        if (resp.status === 'NOT_VISITED') {
            resp.status = 'NOT_ANSWERED';
            updateLegendCounters();
            renderPalette();
        }

        // Meta headers
        elements.currentQDisplayNum.textContent = `Question No. ${currentIndex + 1} of ${currentQuestions.length} (${q.id})`;
        elements.currentQTypeBadge.textContent = q.question_type === 'MCQ' ? 'Multiple Choice (Single Correct)' :
                                                 q.question_type === 'MSQ' ? 'Multiple Select (One or More Correct)' :
                                                 'Numerical / Short Answer (NAT)';
        elements.currentQSubtopic.textContent = `${q.week} › ${q.subtopic}`;
        elements.markPosDisplay.textContent = `Marks for correct: +${q.marks}`;
        elements.markNegDisplay.textContent = 'Negative marks: 0';
        
        // Sources
        const sources = q.source_papers || [];
        elements.qSourceList.textContent = sources.length > 0 ? 
            `${sources[0]} ${sources.length > 1 ? `(+${sources.length - 1} more paper sessions)` : ''}` : 'Official IITM Session';

        // Stem Text
        elements.qStemText.textContent = q.question_text || "[Refer to diagram / matrix statement below]";

        // Stem Images (Diagrams / Formulas / Tables)
        elements.qStemImageBox.innerHTML = '';
        if (q.images && q.images.length > 0) {
            q.images.forEach(imgSrc => {
                const img = document.createElement('img');
                img.src = imgSrc;
                img.alt = "Question Problem Diagram / Formula";
                img.className = "stem-diagram-img";
                elements.qStemImageBox.appendChild(img);
            });
            elements.qStemImageBox.style.display = 'block';
        } else {
            elements.qStemImageBox.style.display = 'none';
        }

        // Render Inputs
        renderAnswerInputs(q, resp);
        updatePaletteActiveState();
    }

    function renderAnswerInputs(q, resp) {
        elements.qInputContainer.innerHTML = '';

        if (q.question_type === 'MCQ' || q.question_type === 'MSQ') {
            const listDiv = document.createElement('div');
            listDiv.className = 'options-list';

            const isMulti = q.question_type === 'MSQ';
            const inputType = isMulti ? 'checkbox' : 'radio';

            (q.options || []).forEach(opt => {
                const row = document.createElement('div');
                row.className = 'option-row';
                const isSelected = resp.selectedOptions.includes(opt.id);
                if (isSelected) row.classList.add('selected');

                const input = document.createElement('input');
                input.type = inputType;
                input.name = `opt_${q.id}`;
                input.value = opt.id;
                input.className = 'option-input';
                input.checked = isSelected;

                const labelSpan = document.createElement('span');
                labelSpan.className = 'option-label';
                labelSpan.textContent = `(${opt.id})`;

                const contentDiv = document.createElement('div');
                contentDiv.className = 'option-content';
                
                if (opt.text) {
                    const txtSpan = document.createElement('span');
                    txtSpan.textContent = opt.text;
                    contentDiv.appendChild(txtSpan);
                }
                if (opt.image) {
                    const img = document.createElement('img');
                    img.src = opt.image;
                    img.alt = `Option ${opt.id} formula`;
                    img.className = 'option-img';
                    contentDiv.appendChild(img);
                }
                if (!opt.text && !opt.image) {
                    contentDiv.textContent = `[Option (${opt.id})]`;
                }

                row.appendChild(input);
                row.appendChild(labelSpan);
                row.appendChild(contentDiv);

                row.addEventListener('click', (e) => {
                    if (e.target !== input) {
                        input.checked = isMulti ? !input.checked : true;
                    }
                    handleOptionToggle(q, opt.id, input.checked, isMulti);
                });

                input.addEventListener('change', () => {
                    handleOptionToggle(q, opt.id, input.checked, isMulti);
                });

                listDiv.appendChild(row);
            });

            elements.qInputContainer.appendChild(listDiv);

        } else if (q.question_type === 'SA') {
            const box = document.createElement('div');
            box.className = 'numeric-input-box';

            const lbl = document.createElement('label');
            lbl.textContent = 'Enter your numerical answer:';

            const inp = document.createElement('input');
            inp.type = 'text';
            inp.className = 'numeric-text-input';
            inp.id = 'natTextInput';
            inp.placeholder = 'e.g. 1.25 or 4';
            inp.value = resp.value || '';
            inp.addEventListener('input', () => {
                resp.value = inp.value.trim();
            });

            const keypad = document.createElement('div');
            keypad.className = 'virtual-keypad';
            const keys = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '.', '-', 'CLEAR', 'BACK'];
            
            keys.forEach(k => {
                const btn = document.createElement('button');
                btn.type = 'button';
                btn.className = `keypad-btn ${k === 'CLEAR' || k === 'BACK' ? 'action' : ''}`;
                btn.textContent = k;
                btn.addEventListener('click', () => {
                    if (k === 'CLEAR') {
                        inp.value = '';
                    } else if (k === 'BACK') {
                        inp.value = inp.value.slice(0, -1);
                    } else {
                        inp.value += k;
                    }
                    resp.value = inp.value.trim();
                });
                keypad.appendChild(btn);
            });

            box.appendChild(lbl);
            box.appendChild(inp);
            box.appendChild(keypad);
            elements.qInputContainer.appendChild(box);
        }
    }

    function handleOptionToggle(q, optId, isChecked, isMulti) {
        const resp = responses[q.id];
        if (isMulti) {
            if (isChecked) {
                if (!resp.selectedOptions.includes(optId)) resp.selectedOptions.push(optId);
            } else {
                resp.selectedOptions = resp.selectedOptions.filter(id => id !== optId);
            }
        } else {
            resp.selectedOptions = isChecked ? [optId] : [];
        }

        const rows = elements.qInputContainer.querySelectorAll('.option-row');
        rows.forEach(r => {
            const input = r.querySelector('input');
            if (input && input.checked) {
                r.classList.add('selected');
            } else {
                r.classList.remove('selected');
            }
        });
    }

    // Render Question Palette Grid
    function renderPalette() {
        elements.paletteGrid.innerHTML = '';
        currentQuestions.forEach((q, idx) => {
            const btn = document.createElement('button');
            btn.className = 'palette-btn';
            btn.textContent = idx + 1;
            
            const resp = responses[q.id];
            applyBadgeStyle(btn, resp.status);

            if (idx === currentIndex) {
                btn.classList.add('active');
            }

            btn.addEventListener('click', () => {
                saveCurrentResponseState(false);
                currentIndex = idx;
                renderCurrentQuestion();
            });

            elements.paletteGrid.appendChild(btn);
        });
    }

    function applyBadgeStyle(btn, status) {
        btn.className = 'palette-btn';
        switch (status) {
            case 'NOT_VISITED':
                btn.classList.add('badge-not-visited');
                break;
            case 'NOT_ANSWERED':
                btn.classList.add('badge-not-answered');
                break;
            case 'ANSWERED':
                btn.classList.add('badge-answered');
                break;
            case 'MARKED':
                btn.classList.add('badge-marked');
                break;
            case 'MARKED_ANSWERED':
                btn.classList.add('badge-marked-answered');
                break;
        }
    }

    function updatePaletteActiveState() {
        const btns = elements.paletteGrid.querySelectorAll('.palette-btn');
        btns.forEach((btn, idx) => {
            if (idx === currentIndex) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });
    }

    function updateLegendCounters() {
        let counts = {
            NOT_VISITED: 0,
            NOT_ANSWERED: 0,
            ANSWERED: 0,
            MARKED: 0,
            MARKED_ANSWERED: 0
        };

        allQuestions.forEach(q => {
            const st = responses[q.id].status;
            counts[st] = (counts[st] || 0) + 1;
        });

        elements.countAnswered.textContent = counts.ANSWERED;
        elements.countNotAnswered.textContent = counts.NOT_ANSWERED;
        elements.countNotVisited.textContent = counts.NOT_VISITED;
        elements.countMarked.textContent = counts.MARKED;
        elements.countMarkedAnswered.textContent = counts.MARKED_ANSWERED;
    }

    function isCurrentQuestionAnswered(q) {
        const resp = responses[q.id];
        if (q.question_type === 'MCQ' || q.question_type === 'MSQ') {
            return resp.selectedOptions && resp.selectedOptions.length > 0;
        } else if (q.question_type === 'SA') {
            return resp.value && resp.value.trim().length > 0;
        }
        return false;
    }

    function saveCurrentResponseState(isMarkReview = false) {
        if (currentQuestions.length === 0) return;
        const q = currentQuestions[currentIndex];
        const resp = responses[q.id];
        const hasAnswer = isCurrentQuestionAnswered(q);

        if (isMarkReview) {
            resp.status = hasAnswer ? 'MARKED_ANSWERED' : 'MARKED';
        } else {
            resp.status = hasAnswer ? 'ANSWERED' : 'NOT_ANSWERED';
        }

        updateLegendCounters();
        renderPalette();
    }

    // Action Handlers
    function handleSaveNext() {
        saveCurrentResponseState(false);
        if (currentIndex < currentQuestions.length - 1) {
            currentIndex++;
            renderCurrentQuestion();
        } else {
            alert("You have reached the last question in this section.");
        }
    }

    function handleMarkReviewNext() {
        saveCurrentResponseState(true);
        if (currentIndex < currentQuestions.length - 1) {
            currentIndex++;
            renderCurrentQuestion();
        } else {
            alert("You have reached the last question in this section.");
        }
    }

    function handleClearResponse() {
        if (currentQuestions.length === 0) return;
        const q = currentQuestions[currentIndex];
        responses[q.id].selectedOptions = [];
        responses[q.id].value = '';
        responses[q.id].status = 'NOT_ANSWERED';

        renderCurrentQuestion();
        updateLegendCounters();
        renderPalette();
    }

    function handlePrevious() {
        saveCurrentResponseState(false);
        if (currentIndex > 0) {
            currentIndex--;
            renderCurrentQuestion();
        }
    }

    // Modals
    function openQuestionPaperModal() {
        elements.qpModalContent.innerHTML = '';
        currentQuestions.forEach((q, idx) => {
            const card = document.createElement('div');
            card.style.marginBottom = '20px';
            card.style.paddingBottom = '15px';
            card.style.borderBottom = '1px solid #e2e8f0';

            const header = document.createElement('h4');
            header.style.color = '#1e3a8a';
            header.textContent = `Q${idx + 1} (${q.id}) [${q.question_type}] - Marks: +${q.marks}`;
            
            const stem = document.createElement('p');
            stem.style.margin = '6px 0 10px 0';
            stem.textContent = q.question_text || "[Refer to diagram/matrix in main view]";

            card.appendChild(header);
            card.appendChild(stem);

            if (q.images && q.images.length > 0) {
                const imgContainer = document.createElement('div');
                imgContainer.style.margin = '8px 0';
                q.images.forEach(imgSrc => {
                    const img = document.createElement('img');
                    img.src = imgSrc;
                    img.style.maxHeight = '140px';
                    img.style.maxWidth = '100%';
                    img.style.display = 'block';
                    img.style.margin = '6px 0';
                    img.style.border = '1px solid #cbd5e1';
                    img.style.borderRadius = '4px';
                    imgContainer.appendChild(img);
                });
                card.appendChild(imgContainer);
            }

            if (q.options && q.options.length > 0) {
                const optList = document.createElement('ul');
                optList.style.listStyle = 'none';
                optList.style.paddingLeft = '10px';
                q.options.forEach(o => {
                    const li = document.createElement('li');
                    li.style.marginBottom = '6px';
                    li.style.display = 'flex';
                    li.style.alignItems = 'center';
                    li.style.gap = '8px';
                    
                    const spanLabel = document.createElement('span');
                    spanLabel.style.fontWeight = 'bold';
                    spanLabel.textContent = `(${o.id})`;
                    li.appendChild(spanLabel);
                    
                    if (o.text) {
                        const spanTxt = document.createElement('span');
                        spanTxt.textContent = o.text;
                        li.appendChild(spanTxt);
                    }
                    if (o.image) {
                        const img = document.createElement('img');
                        img.src = o.image;
                        img.style.maxHeight = '45px';
                        img.style.verticalAlign = 'middle';
                        img.style.border = '1px solid #cbd5e1';
                        img.style.borderRadius = '3px';
                        li.appendChild(img);
                    }
                    optList.appendChild(li);
                });
                card.appendChild(optList);
            }

            elements.qpModalContent.appendChild(card);
        });
        elements.qpModal.style.display = 'flex';
    }

    function openSubmitModal() {
        const weeks = [
            "Week 1 - ML Foundations",
            "Week 2 - Mathematical Foundations",
            "Week 3 - Linear Algebra & Subspaces",
            "Week 4 - Regression & Eigenvalues"
        ];

        elements.submitSummaryTbody.innerHTML = '';
        
        let grandTotal = 0, grandAns = 0, grandNotAns = 0, grandMarked = 0, grandNotVis = 0;

        weeks.forEach(w => {
            const qList = allQuestions.filter(q => q.week === w);
            if (qList.length === 0) return;

            let ans = 0, notAns = 0, marked = 0, notVis = 0;
            qList.forEach(q => {
                const st = responses[q.id].status;
                if (st === 'ANSWERED') ans++;
                else if (st === 'NOT_ANSWERED') notAns++;
                else if (st === 'MARKED' || st === 'MARKED_ANSWERED') marked++;
                else if (st === 'NOT_VISITED') notVis++;
            });

            grandTotal += qList.length;
            grandAns += ans;
            grandNotAns += notAns;
            grandMarked += marked;
            grandNotVis += notVis;

            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td style="text-align: left; font-weight: 600;">${w}</td>
                <td>${qList.length}</td>
                <td style="color: #16a34a; font-weight: bold;">${ans}</td>
                <td style="color: #dc2626; font-weight: bold;">${notAns}</td>
                <td style="color: #7c3aed; font-weight: bold;">${marked}</td>
                <td>${notVis}</td>
            `;
            elements.submitSummaryTbody.appendChild(tr);
        });

        const totalTr = document.createElement('tr');
        totalTr.style.backgroundColor = '#f8fafc';
        totalTr.style.fontWeight = 'bold';
        totalTr.innerHTML = `
            <td style="text-align: left;">Total (All Sections)</td>
            <td>${grandTotal}</td>
            <td style="color: #16a34a;">${grandAns}</td>
            <td style="color: #dc2626;">${grandNotAns}</td>
            <td style="color: #7c3aed;">${grandMarked}</td>
            <td>${grandNotVis}</td>
        `;
        elements.submitSummaryTbody.appendChild(totalTr);

        elements.submitModal.style.display = 'flex';
    }

    function submitExam() {
        if (timerInterval) clearInterval(timerInterval);
        elements.submitModal.style.display = 'none';
        elements.examInterfaceView.style.display = 'none';
        elements.scorecardView.style.display = 'block';

        calculateAndRenderScorecard();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    function calculateAndRenderScorecard() {
        let totalScore = 0;
        let maxMarks = 0;
        let attemptedCount = 0;
        let correctCount = 0;

        const categoryStats = {};

        allQuestions.forEach(q => {
            maxMarks += q.marks;
            const resp = responses[q.id];
            const isAttempted = isCurrentQuestionAnswered(q) || resp.status === 'ANSWERED' || resp.status === 'MARKED_ANSWERED';
            
            const w = q.week;
            const st = q.subtopic;
            categoryStats[w] = categoryStats[w] || {};
            categoryStats[w][st] = categoryStats[w][st] || { total: 0, attempted: 0, correct: 0, incorrect: 0 };
            categoryStats[w][st].total++;

            let isCorrect = false;
            let earned = 0;

            if (isAttempted) {
                attemptedCount++;
                categoryStats[w][st].attempted++;

                const key = q.correct_answer || [];
                if (q.question_type === 'MCQ') {
                    isCorrect = key.length > 0 && key.includes(resp.selectedOptions[0]);
                } else if (q.question_type === 'MSQ') {
                    const sel = new Set(resp.selectedOptions);
                    isCorrect = key.length > 0 && sel.size === key.length && key.every(k => sel.has(k));
                } else if (q.question_type === 'SA') {
                    const v = parseFloat(resp.value);
                    isCorrect = !Number.isNaN(v) && key.some(ans => {
                        const m = ans.match(/^\s*(-?[\d.]+)\s*to\s*(-?[\d.]+)/);
                        if (m) return v >= parseFloat(m[1]) && v <= parseFloat(m[2]);
                        const exact = parseFloat(ans);
                        return !Number.isNaN(exact) && Math.abs(v - exact) < 1e-6;
                    });
                }

                if (isCorrect) {
                    correctCount++;
                    earned = q.marks;
                    totalScore += earned;
                    categoryStats[w][st].correct++;
                } else {
                    earned = 0; // Section Negative Marks : 0 in IITM MLF
                    categoryStats[w][st].incorrect++;
                }
            }

            resp.evaluation = {
                isAttempted,
                isCorrect,
                marksAwarded: earned
            };
        });

        // Set exam submitted and stop timer
        isExamSubmitted = true;
        stopTimer();

        // Record Test Attempt in Auth & Admin storage
        const accuracy = attemptedCount > 0 ? Math.round((correctCount / attemptedCount) * 100) : 0;
        if (window.MLFAuth) {
            window.MLFAuth.recordTestAttempt({
                section: 'Full Syllabus (All Weeks)',
                totalQuestions: allQuestions.length,
                attempted: attemptedCount,
                correct: correctCount,
                score: totalScore,
                maxMarks: maxMarks,
                accuracy: accuracy,
                timeSpent: `${Math.round((180 * 60 - totalSeconds) / 60)} mins`
            });
            if (window.MLFAdmin) {
                window.MLFAdmin.renderOverview();
                window.MLFAdmin.renderAttemptsTable();
                window.MLFAdmin.renderUsersTable();
            }
        }

        // Render Metric Cards
        elements.resTotalScore.textContent = totalScore;
        elements.resMaxMarks.textContent = maxMarks;
        elements.resAccuracy.textContent = `${accuracy}%`;
        elements.resAttempted.textContent = `${attemptedCount} / ${allQuestions.length}`;

        // Render Category Breakdown Table
        elements.categoryPerfTbody.innerHTML = '';
        Object.keys(categoryStats).sort().forEach(w => {
            Object.keys(categoryStats[w]).sort().forEach(st => {
                const s = categoryStats[w][st];
                const acc = s.attempted > 0 ? Math.round((s.correct / s.attempted) * 100) : 0;
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td style="font-weight: 600;">${w}</td>
                    <td>${st}</td>
                    <td>${s.total}</td>
                    <td>${s.attempted}</td>
                    <td style="color: #16a34a; font-weight: bold;">${s.correct}</td>
                    <td style="color: #dc2626; font-weight: bold;">${s.incorrect}</td>
                    <td style="font-weight: bold;">${acc}%</td>
                `;
                elements.categoryPerfTbody.appendChild(tr);
            });
        });

        // Render Detailed Review List
        renderDetailedReview('ALL');
    }

    function renderDetailedReview(filter) {
        elements.reviewQuestionsList.innerHTML = '';

        allQuestions.forEach((q, idx) => {
            const resp = responses[q.id];
            const evalData = resp.evaluation || {};

            let matchFilter = true;
            if (filter === 'CORRECT') matchFilter = evalData.isCorrect;
            else if (filter === 'INCORRECT') matchFilter = evalData.isAttempted && !evalData.isCorrect;
            else if (filter === 'UNATTEMPTED') matchFilter = !evalData.isAttempted;

            if (!matchFilter) return;

            const card = document.createElement('div');
            card.className = `review-q-card ${evalData.isCorrect ? 'status-correct' : evalData.isAttempted ? 'status-incorrect' : 'status-unattempted'}`;

            const header = document.createElement('div');
            header.className = 'review-q-header';
            header.innerHTML = `
                <span>Q${idx + 1} (${q.id}) — ${q.week} › ${q.subtopic}</span>
                <span>${evalData.isCorrect ? `<span style="color: #16a34a;">✔ Correct (+${evalData.marksAwarded})</span>` :
                       evalData.isAttempted ? `<span style="color: #dc2626;">✖ Incorrect (${evalData.marksAwarded})</span>` :
                       '<span style="color: #64748b;">Not Attempted (0)</span>'}</span>
            `;

            const stem = document.createElement('div');
            stem.className = 'review-q-stem';
            stem.textContent = q.question_text || "[Diagram problem]";

            // Stem Diagrams
            const stemImgsBox = document.createElement('div');
            if (q.images && q.images.length > 0) {
                stemImgsBox.style.margin = '10px 0';
                q.images.forEach(imgSrc => {
                    const img = document.createElement('img');
                    img.src = imgSrc;
                    img.className = 'stem-diagram-img';
                    img.style.maxHeight = '220px';
                    stemImgsBox.appendChild(img);
                });
            }

            // Options List with Visual Feedback
            const optsContainer = document.createElement('div');
            if (q.options && q.options.length > 0) {
                optsContainer.className = 'review-options-container';
                optsContainer.style.margin = '12px 0';
                optsContainer.style.display = 'flex';
                optsContainer.style.flexDirection = 'column';
                optsContainer.style.gap = '8px';

                q.options.forEach(o => {
                    const optRow = document.createElement('div');
                    optRow.className = 'review-option-row';
                    optRow.style.padding = '8px 12px';
                    optRow.style.borderRadius = '5px';
                    optRow.style.border = '1px solid #e2e8f0';
                    optRow.style.display = 'flex';
                    optRow.style.alignItems = 'center';
                    optRow.style.gap = '10px';
                    optRow.style.backgroundColor = '#ffffff';

                    const isOfficialCorrect = (q.correct_answer || []).includes(o.id);
                    const isCandidateSelected = (resp.selectedOptions || []).includes(o.id);

                    if (isOfficialCorrect) {
                        optRow.style.borderColor = '#22c55e';
                        optRow.style.backgroundColor = '#f0fdf4';
                    } else if (isCandidateSelected && !isOfficialCorrect) {
                        optRow.style.borderColor = '#ef4444';
                        optRow.style.backgroundColor = '#fef2f2';
                    }

                    const badge = document.createElement('span');
                    badge.style.fontWeight = 'bold';
                    badge.style.fontSize = '13px';
                    badge.textContent = `(${o.id})`;
                    if (isOfficialCorrect) badge.style.color = '#15803d';
                    optRow.appendChild(badge);

                    const optBody = document.createElement('div');
                    optBody.style.flex = '1';
                    if (o.text) {
                        const tSpan = document.createElement('span');
                        tSpan.textContent = o.text;
                        optBody.appendChild(tSpan);
                    }
                    if (o.image) {
                        const img = document.createElement('img');
                        img.src = o.image;
                        img.className = 'option-img';
                        img.style.display = 'block';
                        img.style.marginTop = '4px';
                        optBody.appendChild(img);
                    }
                    optRow.appendChild(optBody);

                    if (isOfficialCorrect) {
                        const tag = document.createElement('span');
                        tag.style.fontSize = '11px';
                        tag.style.fontWeight = '700';
                        tag.style.color = '#15803d';
                        tag.style.backgroundColor = '#dcfce7';
                        tag.style.padding = '2px 8px';
                        tag.style.borderRadius = '12px';
                        tag.textContent = '✔ Correct Option';
                        optRow.appendChild(tag);
                    }
                    if (isCandidateSelected) {
                        const tag2 = document.createElement('span');
                        tag2.style.fontSize = '11px';
                        tag2.style.fontWeight = '700';
                        tag2.style.color = isOfficialCorrect ? '#15803d' : '#b91c1c';
                        tag2.style.backgroundColor = isOfficialCorrect ? '#dcfce7' : '#fee2e2';
                        tag2.style.padding = '2px 8px';
                        tag2.style.borderRadius = '12px';
                        tag2.textContent = isOfficialCorrect ? 'Your Choice (Correct)' : 'Your Choice (Incorrect)';
                        optRow.appendChild(tag2);
                    }

                    optsContainer.appendChild(optRow);
                });
            }

            const ansBox = document.createElement('div');
            ansBox.className = 'review-q-ans-box';
            
            const yourAns = q.question_type === 'SA' ? (resp.value || 'None') : (resp.selectedOptions.join(', ') || 'None');
            const officialAns = (q.correct_answer || []).join(', ') || 'Official Answer Key in Paper';

            const respDiv = document.createElement('div');
            const respBold = document.createElement('strong');
            respBold.textContent = 'Your Response: ';
            respDiv.appendChild(respBold);
            respDiv.appendChild(document.createTextNode(yourAns));

            const offDiv = document.createElement('div');
            const offBold = document.createElement('strong');
            offBold.textContent = 'Official Correct Answer: ';
            const offSpan = document.createElement('span');
            offSpan.style.color = '#16a34a';
            offSpan.style.fontWeight = 'bold';
            offSpan.textContent = officialAns;
            offDiv.appendChild(offBold);
            offDiv.appendChild(offSpan);

            ansBox.appendChild(respDiv);
            ansBox.appendChild(offDiv);

            if (q.explanation) {
                const expDiv = document.createElement('div');
                expDiv.style.marginTop = '6px';
                expDiv.style.color = '#475569';
                const expBold = document.createElement('strong');
                expBold.textContent = 'Explanation: ';
                expDiv.appendChild(expBold);
                expDiv.appendChild(document.createTextNode(q.explanation));
                ansBox.appendChild(expDiv);
            }

            card.appendChild(header);
            card.appendChild(stem);
            if (q.images && q.images.length > 0) card.appendChild(stemImgsBox);
            if (q.options && q.options.length > 0) card.appendChild(optsContainer);
            card.appendChild(ansBox);
            elements.reviewQuestionsList.appendChild(card);
        });
    }

    // Event Bindings
    function bindEvents() {
        // Section Tab Clicks
        elements.sectionTabs.querySelectorAll('.sec-tab').forEach(tab => {
            tab.addEventListener('click', () => {
                elements.sectionTabs.querySelectorAll('.sec-tab').forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                currentWeekFilter = tab.dataset.week;
                currentSubtopicFilter = 'ALL';
                buildSubtopicDropdown();
                applyFilter();
            });
        });

        // Subtopic Select
        elements.subtopicSelect.addEventListener('change', (e) => {
            currentSubtopicFilter = e.target.value;
            applyFilter();
        });

        // Navigation Controls
        elements.btnSaveNext.addEventListener('click', handleSaveNext);
        elements.btnMarkReviewNext.addEventListener('click', handleMarkReviewNext);
        elements.btnClearResponse.addEventListener('click', handleClearResponse);
        elements.btnPrevious.addEventListener('click', handlePrevious);

        // Timer Pause/Resume
        elements.pauseTimerBtn.addEventListener('click', () => {
            isPaused = !isPaused;
            elements.pauseTimerBtn.textContent = isPaused ? '▶' : '⏸';
            elements.pauseTimerBtn.title = isPaused ? 'Resume Timer' : 'Pause Timer';
        });

        // Modals
        elements.viewQPBtn.addEventListener('click', openQuestionPaperModal);
        elements.closeQpModal.addEventListener('click', () => elements.qpModal.style.display = 'none');
        elements.closeQpModalBtn.addEventListener('click', () => elements.qpModal.style.display = 'none');

        elements.viewInstBtn.addEventListener('click', () => elements.instModal.style.display = 'flex');
        elements.closeInstModal.addEventListener('click', () => elements.instModal.style.display = 'none');
        elements.closeInstModalBtn.addEventListener('click', () => elements.instModal.style.display = 'none');

        elements.btnSubmitTest.addEventListener('click', openSubmitModal);
        elements.closeSubmitModal.addEventListener('click', () => elements.submitModal.style.display = 'none');
        elements.cancelSubmitBtn.addEventListener('click', () => elements.submitModal.style.display = 'none');
        elements.confirmSubmitBtn.addEventListener('click', submitExam);

        // Restart Test
        elements.btnRestartTest.addEventListener('click', () => {
            if (confirm("Restart test? All responses will be cleared.")) {
                location.reload();
            }
        });

        // Review Filter Tabs
        document.querySelectorAll('.review-filter-tab').forEach(tab => {
            tab.addEventListener('click', () => {
                document.querySelectorAll('.review-filter-tab').forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                renderDetailedReview(tab.dataset.filter);
            });
        });

        // ==================== AUTH & ADMIN DASHBOARD EVENTS ====================
        // Auth Tab Toggle
        elements.tabLoginBtn.addEventListener('click', () => {
            elements.tabLoginBtn.classList.add('active');
            elements.tabSignupBtn.classList.remove('active');
            elements.formLogin.style.display = 'block';
            elements.formSignup.style.display = 'none';
            hideAuthAlert();
        });

        elements.tabSignupBtn.addEventListener('click', () => {
            elements.tabSignupBtn.classList.add('active');
            elements.tabLoginBtn.classList.remove('active');
            elements.formLogin.style.display = 'none';
            elements.formSignup.style.display = 'block';
            hideAuthAlert();
        });

        // Form Login
        elements.formLogin.addEventListener('submit', (e) => {
            e.preventDefault();
            const idVal = document.getElementById('loginIdentifier').value;
            const passVal = document.getElementById('loginPassword').value;
            const rememberMe = document.getElementById('loginRememberMe').checked;

            const res = window.MLFAuth.login(idVal, passVal, rememberMe);
            if (res.success) {
                checkAuthAndSetupUI();
            } else {
                showAuthAlert(res.error || 'Login failed.');
            }
        });

        // Form Signup
        elements.formSignup.addEventListener('submit', (e) => {
            e.preventDefault();
            const name = document.getElementById('signupName').value;
            const email = document.getElementById('signupEmail').value;
            const rollNo = document.getElementById('signupRoll').value;
            const password = document.getElementById('signupPassword').value;
            const role = document.getElementById('signupRole').value;

            const res = window.MLFAuth.signUp(name, email, rollNo, password, role);
            if (res.success) {
                checkAuthAndSetupUI();
            } else {
                showAuthAlert(res.error || 'Registration failed.');
            }
        });

        // Quick Demo Logins
        elements.btnQuickStudent.addEventListener('click', () => {
            document.getElementById('loginIdentifier').value = 'student@iitm.ac.in';
            document.getElementById('loginPassword').value = 'Student@123';
            const res = window.MLFAuth.login('student@iitm.ac.in', 'Student@123', true);
            if (res.success) checkAuthAndSetupUI();
        });

        elements.btnQuickAdmin.addEventListener('click', () => {
            document.getElementById('loginIdentifier').value = 'admin@iitm.ac.in';
            document.getElementById('loginPassword').value = 'Admin@123';
            const res = window.MLFAuth.login('admin@iitm.ac.in', 'Admin@123', true);
            if (res.success) checkAuthAndSetupUI();
        });

        // Logout
        elements.btnLogout.addEventListener('click', () => {
            if (confirm("Sign out of MLF CBT portal?")) {
                window.MLFAuth.logout();
                resetExamState();
                elements.authModal.style.display = 'flex';
                elements.btnToggleAdminView.style.display = 'none';
                elements.btnToggleExamView.style.display = 'none';
                elements.examInterfaceView.style.display = 'block';
                elements.adminDashboardView.style.display = 'none';
                elements.scorecardView.style.display = 'none';
            }
        });

        // Switch to Admin Dashboard View
        elements.btnToggleAdminView.addEventListener('click', () => {
            elements.examInterfaceView.style.display = 'none';
            elements.scorecardView.style.display = 'none';
            elements.adminDashboardView.style.display = 'block';
            elements.btnToggleAdminView.style.display = 'none';
            elements.btnToggleExamView.style.display = 'inline-block';
            if (window.MLFAdmin) {
                window.MLFAdmin.renderOverview();
                window.MLFAdmin.renderUsersTable();
                window.MLFAdmin.renderAttemptsTable();
                window.MLFAdmin.renderQuestionsTable();
                window.MLFAdmin.renderSyllabusAnalytics();
            }
        });

        // Switch back to Exam View / Scorecard View
        elements.btnToggleExamView.addEventListener('click', () => {
            elements.adminDashboardView.style.display = 'none';
            elements.btnToggleExamView.style.display = 'none';
            const curUser = window.MLFAuth ? window.MLFAuth.getCurrentUser() : null;
            if (curUser && curUser.role === 'admin') {
                elements.btnToggleAdminView.style.display = 'inline-block';
            }

            if (isExamSubmitted) {
                elements.scorecardView.style.display = 'block';
                elements.examInterfaceView.style.display = 'none';
            } else {
                elements.examInterfaceView.style.display = 'block';
                elements.scorecardView.style.display = 'none';
                startTimer();
            }
        });
    }

    // Run on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
