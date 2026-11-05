// Authentication, Role-Based Access Control & User Management System
(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        define([], factory);
    } else if (typeof module === 'object' && module.exports) {
        module.exports = factory();
    } else {
        root.MLFAuth = factory();
    }
}(typeof self !== 'undefined' ? self : this, function () {
    'use strict';

    const USERS_KEY = 'mlf_users_v1';
    const SESSION_KEY = 'mlf_current_user_v1';
    const ATTEMPTS_KEY = 'mlf_test_attempts_v1';

    // Seed default administrative and demo student accounts
    function seedDefaultUsers() {
        const existing = localStorage.getItem(USERS_KEY);
        if (!existing) {
            const defaults = [
                {
                    id: 'usr_admin_01',
                    name: 'Faculty Administrator',
                    email: 'admin@iitm.ac.in',
                    rollNo: 'ADMIN-001',
                    password: 'Admin@123',
                    role: 'admin',
                    status: 'active',
                    createdAt: '2026-11-01T10:00:00Z',
                    testsTaken: 0,
                    bestScore: 0
                },
                {
                    id: 'usr_student_01',
                    name: 'Avesh Dubey',
                    email: 'student@iitm.ac.in',
                    rollNo: '24DS109284',
                    password: 'Student@123',
                    role: 'student',
                    status: 'active',
                    createdAt: '2026-11-02T12:30:00Z',
                    testsTaken: 3,
                    bestScore: 54
                },
                {
                    id: 'usr_student_02',
                    name: 'Priya Sharma',
                    email: 'priya.s@iitm.ac.in',
                    rollNo: '24DS105412',
                    password: 'Student@123',
                    role: 'student',
                    status: 'active',
                    createdAt: '2026-11-03T14:15:00Z',
                    testsTaken: 2,
                    bestScore: 48
                },
                {
                    id: 'usr_student_03',
                    name: 'Rahul Verma',
                    email: 'rahul.v@iitm.ac.in',
                    rollNo: '24DS107823',
                    password: 'Student@123',
                    role: 'student',
                    status: 'active',
                    createdAt: '2026-11-04T09:45:00Z',
                    testsTaken: 1,
                    bestScore: 36
                }
            ];
            localStorage.setItem(USERS_KEY, JSON.stringify(defaults));
        }

        const existingAttempts = localStorage.getItem(ATTEMPTS_KEY);
        if (!existingAttempts) {
            const sampleAttempts = [
                {
                    id: 'att_001',
                    userId: 'usr_student_01',
                    userName: 'Avesh Dubey',
                    userRoll: '24DS109284',
                    timestamp: '2026-11-04T16:20:00Z',
                    section: 'All Weeks',
                    totalQuestions: 210,
                    attempted: 24,
                    correct: 18,
                    score: 54,
                    maxMarks: 630,
                    accuracy: 75,
                    timeSpent: '45 mins'
                },
                {
                    id: 'att_002',
                    userId: 'usr_student_02',
                    userName: 'Priya Sharma',
                    userRoll: '24DS105412',
                    timestamp: '2026-11-05T09:10:00Z',
                    section: 'Week 1 - ML Foundations',
                    totalQuestions: 95,
                    attempted: 20,
                    correct: 16,
                    score: 48,
                    maxMarks: 285,
                    accuracy: 80,
                    timeSpent: '32 mins'
                },
                {
                    id: 'att_003',
                    userId: 'usr_student_03',
                    userName: 'Rahul Verma',
                    userRoll: '24DS107823',
                    timestamp: '2026-11-05T11:40:00Z',
                    section: 'Week 3 - Linear Algebra',
                    totalQuestions: 63,
                    attempted: 15,
                    correct: 12,
                    score: 36,
                    maxMarks: 189,
                    accuracy: 80,
                    timeSpent: '28 mins'
                }
            ];
            localStorage.setItem(ATTEMPTS_KEY, JSON.stringify(sampleAttempts));
        }
    }

    // Helper: read all users
    function getUsers() {
        try {
            return JSON.parse(localStorage.getItem(USERS_KEY)) || [];
        } catch (e) {
            return [];
        }
    }

    // Helper: save all users
    function setUsers(users) {
        localStorage.setItem(USERS_KEY, JSON.stringify(users));
    }

    // Helper: read attempts
    function getAttempts() {
        try {
            return JSON.parse(localStorage.getItem(ATTEMPTS_KEY)) || [];
        } catch (e) {
            return [];
        }
    }

    // Helper: save attempts
    function setAttempts(attempts) {
        localStorage.setItem(ATTEMPTS_KEY, JSON.stringify(attempts));
    }

    // Public API
    const Auth = {
        init: function () {
            seedDefaultUsers();
        },

        getCurrentUser: function () {
            try {
                const sessionStr = sessionStorage.getItem(SESSION_KEY) || localStorage.getItem(SESSION_KEY);
                return sessionStr ? JSON.parse(sessionStr) : null;
            } catch (e) {
                return null;
            }
        },

        login: function (identifier, password, rememberMe) {
            seedDefaultUsers();
            const users = getUsers();
            const cleanId = (identifier || '').trim().toLowerCase();
            const cleanPass = (password || '').trim();

            const user = users.find(u => 
                (u.email.toLowerCase() === cleanId || u.rollNo.toLowerCase() === cleanId) &&
                u.password === cleanPass
            );

            if (!user) {
                return { success: false, error: 'Invalid Email/Roll Number or Password.' };
            }

            if (user.status === 'suspended') {
                return { success: false, error: 'This user account has been suspended by the administrator.' };
            }

            // Exclude password from active session
            const safeUser = Object.assign({}, user);
            delete safeUser.password;

            const sessionData = JSON.stringify(safeUser);
            sessionStorage.setItem(SESSION_KEY, sessionData);
            if (rememberMe) {
                localStorage.setItem(SESSION_KEY, sessionData);
            }

            return { success: true, user: safeUser };
        },

        signUp: function (name, email, rollNo, password, role) {
            seedDefaultUsers();
            const users = getUsers();
            const cleanEmail = (email || '').trim().toLowerCase();
            const cleanRoll = (rollNo || '').trim().toUpperCase();

            if (!name || name.trim().length < 2) {
                return { success: false, error: 'Please enter a valid full name.' };
            }
            if (!cleanEmail || !cleanEmail.includes('@')) {
                return { success: false, error: 'Please enter a valid email address.' };
            }
            if (!cleanRoll || cleanRoll.length < 4) {
                return { success: false, error: 'Please enter a valid IITM Roll Number (e.g. 24DS100000).' };
            }
            if (!password || password.length < 6) {
                return { success: false, error: 'Password must be at least 6 characters long.' };
            }

            // Check duplicates
            const exists = users.some(u => 
                u.email.toLowerCase() === cleanEmail || u.rollNo.toUpperCase() === cleanRoll
            );
            if (exists) {
                return { success: false, error: 'An account with this Email or Roll Number already exists.' };
            }

            const newUser = {
                id: 'usr_' + Date.now().toString(36),
                name: name.trim(),
                email: cleanEmail,
                rollNo: cleanRoll,
                password: password,
                role: role === 'admin' ? 'admin' : 'student',
                status: 'active',
                createdAt: new Date().toISOString(),
                testsTaken: 0,
                bestScore: 0
            };

            users.push(newUser);
            setUsers(users);

            // Auto-login after sign-up
            const safeUser = Object.assign({}, newUser);
            delete safeUser.password;
            sessionStorage.setItem(SESSION_KEY, JSON.stringify(safeUser));

            return { success: true, user: safeUser };
        },

        logout: function () {
            sessionStorage.removeItem(SESSION_KEY);
            localStorage.removeItem(SESSION_KEY);
            return true;
        },

        // Admin User Management
        getAllUsers: function () {
            seedDefaultUsers();
            return getUsers().map(u => {
                const copy = Object.assign({}, u);
                delete copy.password;
                return copy;
            });
        },

        addUserByAdmin: function (userData) {
            return Auth.signUp(
                userData.name,
                userData.email,
                userData.rollNo,
                userData.password || 'Student@123',
                userData.role || 'student'
            );
        },

        toggleUserStatus: function (userId) {
            const users = getUsers();
            const idx = users.findIndex(u => u.id === userId);
            if (idx === -1) return { success: false, error: 'User not found.' };

            if (users[idx].role === 'admin') {
                return { success: false, error: 'Cannot suspend an Administrator account.' };
            }

            users[idx].status = users[idx].status === 'active' ? 'suspended' : 'active';
            setUsers(users);
            return { success: true, newStatus: users[idx].status };
        },

        resetUserPassword: function (userId, newPassword) {
            const users = getUsers();
            const idx = users.findIndex(u => u.id === userId);
            if (idx === -1) return { success: false, error: 'User not found.' };

            users[idx].password = newPassword || 'Student@123';
            setUsers(users);
            return { success: true };
        },

        deleteUser: function (userId) {
            let users = getUsers();
            const target = users.find(u => u.id === userId);
            if (!target) return { success: false, error: 'User not found.' };
            if (target.role === 'admin') return { success: false, error: 'Cannot delete an Administrator account.' };

            users = users.filter(u => u.id !== userId);
            setUsers(users);
            return { success: true };
        },

        // Test Attempts Recording
        recordTestAttempt: function (attemptData) {
            const attempts = getAttempts();
            const curUser = Auth.getCurrentUser();
            
            const newAttempt = {
                id: 'att_' + Date.now().toString(36),
                userId: curUser ? curUser.id : 'guest',
                userName: curUser ? curUser.name : 'Guest Candidate',
                userRoll: curUser ? curUser.rollNo : '24DSXXXXXX',
                timestamp: new Date().toISOString(),
                section: attemptData.section || 'All Weeks',
                totalQuestions: attemptData.totalQuestions || 210,
                attempted: attemptData.attempted || 0,
                correct: attemptData.correct || 0,
                score: attemptData.score || 0,
                maxMarks: attemptData.maxMarks || 630,
                accuracy: attemptData.accuracy || 0,
                timeSpent: attemptData.timeSpent || 'N/A'
            };

            attempts.unshift(newAttempt);
            setAttempts(attempts);

            // Update user stats
            if (curUser) {
                const users = getUsers();
                const uIdx = users.findIndex(u => u.id === curUser.id);
                if (uIdx !== -1) {
                    users[uIdx].testsTaken = (users[uIdx].testsTaken || 0) + 1;
                    if (newAttempt.score > (users[uIdx].bestScore || 0)) {
                        users[uIdx].bestScore = newAttempt.score;
                    }
                    setUsers(users);
                }
            }

            return newAttempt;
        },

        getAllAttempts: function () {
            seedDefaultUsers();
            return getAttempts();
        },

        resetAllData: function () {
            localStorage.removeItem(USERS_KEY);
            localStorage.removeItem(SESSION_KEY);
            localStorage.removeItem(ATTEMPTS_KEY);
            sessionStorage.removeItem(SESSION_KEY);
            seedDefaultUsers();
            return true;
        }
    };

    Auth.init();
    return Auth;
}));
