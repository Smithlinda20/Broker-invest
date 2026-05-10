// Dashboard JavaScript

const API_BASE_URL = '/api';

// Initialize dashboard on page load
document.addEventListener('DOMContentLoaded', function() {
    initializeDashboard();
});

async function initializeDashboard() {
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    const profile = JSON.parse(localStorage.getItem('profile') || '{}');
    
    if (!user.id) {
        window.location.href = '/login';
        return;
    }

    // Set username in display
    document.getElementById('username').textContent = user.username;
    
    // Load investment plans
    loadInvestmentPlans();
    
    // Load user data
    loadUserData();
    
    // Load payment wallets
    loadPaymentWallets();
    
    // Set referral code
    if (profile.referral_code) {
        document.getElementById('referralCodeDisplay').value = profile.referral_code;
    }
}

// Load investment plans
async function loadInvestmentPlans() {
    try {
        const response = await fetch(`${API_BASE_URL}/investments/plans/`);
        if (response.ok) {
            const plans = await response.json();
            displayPlans(plans);
        }
    } catch (error) {
        console.error('Error loading plans:', error);
    }
}

// Display investment plans
function displayPlans(plans) {
    const container = document.getElementById('plansContainer');
    if (!container) return;

    container.innerHTML = '';
    
    plans.forEach(plan => {
        const card = document.createElement('div');
        card.className = 'plan-card-dashboard';
        card.innerHTML = `
            <div class="plan-name">${plan.name}</div>
            <div class="plan-return-big">${plan.daily_return_percentage}%</div>
            <p>Daily Return</p>
            <ul class="plan-details-list">
                <li>Min: $${parseFloat(plan.min_amount).toFixed(2)}</li>
                <li>Max: $${plan.max_amount === '999999999.99' ? 'Unlimited' : parseFloat(plan.max_amount).toFixed(2)}</li>
                <li>Duration: ${plan.duration_days} Days</li>
            </ul>
            <button class="btn btn-primary btn-block" onclick="openInvestmentForm('${plan.id}', ${plan.min_amount}, ${plan.max_amount})">
                Invest Now
            </button>
        `;
        container.appendChild(card);
    });
}

// Open investment form
function openInvestmentForm(planId, minAmount, maxAmount) {
    document.getElementById('selectedPlanId').value = planId;
    document.getElementById('investmentAmount').min = minAmount;
    document.getElementById('investmentAmount').max = maxAmount;
    document.getElementById('investmentFormContainer').classList.remove('hidden');
    document.getElementById('investmentFormContainer').scrollIntoView({ behavior: 'smooth' });
}

// Close investment form
function closeInvestmentForm() {
    document.getElementById('investmentFormContainer').classList.add('hidden');
    document.getElementById('investmentForm').reset();
}

// Submit investment form
document.addEventListener('DOMContentLoaded', function() {
    const investmentForm = document.getElementById('investmentForm');
    if (investmentForm) {
        investmentForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const planId = document.getElementById('selectedPlanId').value;
            const amount = document.getElementById('investmentAmount').value;
            const pin = document.getElementById('investmentPin').value;
            
            try {
                const response = await fetch(`${API_BASE_URL}/investments/active/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${localStorage.getItem('token')}`
                    },
                    body: JSON.stringify({
                        plan_id: planId,
                        amount: amount
                    })
                });

                if (response.ok) {
                    alert('Investment created successfully!');
                    closeInvestmentForm();
                    loadUserData();
                } else {
                    const error = await response.json();
                    alert('Error: ' + JSON.stringify(error));
                }
            } catch (error) {
                alert('Error: ' + error.message);
            }
        });
    }
});

// Load user data
async function loadUserData() {
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    const profile = JSON.parse(localStorage.getItem('profile') || '{}');

    // Update balance display
    const balanceDisplay = document.getElementById('dashboardBalance');
    if (balanceDisplay) {
        balanceDisplay.textContent = `$${parseFloat(profile.balance || 0).toFixed(2)}`;
    }
    
    const topBarBalance = document.getElementById('balanceDisplay');
    if (topBarBalance) {
        topBarBalance.textContent = `Balance: $${parseFloat(profile.balance || 0).toFixed(2)}`;
    }

    // Load investments
    try {
        const response = await fetch(`${API_BASE_URL}/investments/active/my_investments/`, {
            headers: {
                'Authorization': `Bearer ${user.id}`
            }
        });

        if (response.ok) {
            const investments = await response.json();
            displayInvestments(investments);
            updateDashboardStats(investments, profile);
        }
    } catch (error) {
        console.error('Error loading investments:', error);
    }

    // Load referrals
    loadReferrals();
    
    // Load history
    loadHistory();
}

// Display user investments
function displayInvestments(investments) {
    const container = document.getElementById('investmentsList');
    if (!container) return;

    if (investments.length === 0) {
        container.innerHTML = '<p class="empty-state">No active investments yet</p>';
        return;
    }

    container.innerHTML = '';
    
    investments.forEach(investment => {
        const item = document.createElement('div');
        item.className = 'investment-item';
        item.innerHTML = `
            <div class="investment-info">
                <h4>${investment.plan.name}</h4>
                <div class="investment-details">
                    <span>Amount: $${parseFloat(investment.amount).toFixed(2)}</span>
                    <span>Daily: ${investment.plan.daily_return_percentage}%</span>
                    <span>Status: ${investment.status}</span>
                </div>
            </div>
            <div class="investment-earnings">
                <div class="investment-earnings-amount">$${parseFloat(investment.earned).toFixed(2)}</div>
                <small>Earned</small>
            </div>
        `;
        container.appendChild(item);
    });
}

// Update dashboard statistics
function updateDashboardStats(investments, profile) {
    document.getElementById('activeInvestments').textContent = investments.length;
    
    const totalEarned = investments.reduce((sum, inv) => sum + parseFloat(inv.earned || 0), 0);
    document.getElementById('totalEarned').textContent = `$${totalEarned.toFixed(2)}`;
    
    document.getElementById('referralEarnings').textContent = `$${parseFloat(profile.referral_earnings || 0).toFixed(2)}`;
}

// Load payment wallets
async function loadPaymentWallets() {
    try {
        const response = await fetch(`${API_BASE_URL}/admin/payment-wallets/`);
        if (response.ok) {
            const wallets = await response.json();
            storeWalletsForWithdrawal(wallets);
            displayWalletInvestmentInfo(wallets);
        }
    } catch (error) {
        console.error('Error loading wallets:', error);
    }
}

// Store wallets for withdrawal section
function storeWalletsForWithdrawal(wallets) {
    window.paymentWallets = {};
    wallets.forEach(wallet => {
        window.paymentWallets[wallet.crypto_type] = {
            address: wallet.wallet_address,
            network: wallet.network,
            logo_url: wallet.logo_url,
            qr_code: wallet.qr_code
        };
    });
}

// Display wallet information in investment section
function displayWalletInvestmentInfo(wallets) {
    const investmentSection = document.getElementById('invest-section');
    if (!investmentSection) return;
    
    let walletInfo = '<div style="margin-top:2rem;padding:1.5rem;background:var(--navy-card);border:1px solid var(--border-light);border-radius:var(--radius);">';
    walletInfo += '<h3 style="margin-top:0;color:var(--gold);">💳 Payment Wallets</h3>';
    walletInfo += '<p style="font-size:0.9rem;color:var(--text-secondary);margin-bottom:1rem;">Send payment to one of these addresses to complete your investment:</p>';
    walletInfo += '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:1rem;">';
    
    wallets.forEach(wallet => {
        walletInfo += `
            <div style="padding:1rem;border:1px solid var(--border-light);border-radius:8px;background:rgba(15,23,42,0.5);">
                <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.75rem;">
                    ${wallet.logo_url ? `<img src="${wallet.logo_url}" alt="${wallet.crypto_type}" style="width:24px;height:24px;">` : ''}
                    <strong>${wallet.crypto_type}</strong>
                </div>
                <p style="font-size:0.8rem;color:var(--text-muted);margin:0.5rem 0;">Network: ${wallet.network}</p>
                <p style="font-size:0.75rem;color:var(--text-secondary);word-break:break-all;margin:0.5rem 0;font-family:monospace;background:rgba(0,0,0,0.2);padding:0.5rem;border-radius:4px;">${wallet.wallet_address}</p>
                ${wallet.qr_code ? `<img src="${wallet.qr_code}" alt="QR Code" style="width:100%;max-width:150px;margin-top:0.5rem;border-radius:4px;">` : ''}
            </div>
        `;
    });
    
    walletInfo += '</div></div>';
    
    const form = investmentSection.querySelector('#investmentForm');
    if (form) {
        form.insertAdjacentHTML('afterend', walletInfo);
    }
}

// Setup withdrawal form
document.addEventListener('DOMContentLoaded', function() {
    const withdrawalMethod = document.getElementById('withdrawalMethod');
    if (withdrawalMethod) {
        withdrawalMethod.addEventListener('change', function() {
            const cryptoOptions = document.getElementById('cryptoOptions');
            const bankOptions = document.getElementById('bankOptions');
            const walletDisplay = document.getElementById('walletDisplay');
            
            if (this.value === 'crypto') {
                cryptoOptions.classList.remove('hidden');
                bankOptions.classList.add('hidden');
                
                // Setup crypto type change
                const cryptoRadios = document.querySelectorAll('input[name="cryptoType"]');
                cryptoRadios.forEach(radio => {
                    radio.addEventListener('change', function() {
                        if (window.paymentWallets && window.paymentWallets[this.value]) {
                            const wallet = window.paymentWallets[this.value];
                            document.getElementById('walletCurrency').textContent = this.value;
                            document.getElementById('walletNetwork').textContent = wallet.network;
                            document.getElementById('walletAddress').value = wallet.address;
                            walletDisplay.classList.remove('hidden');
                        }
                    });
                });
            } else if (this.value === 'bank') {
                cryptoOptions.classList.add('hidden');
                bankOptions.classList.remove('hidden');
                walletDisplay.classList.add('hidden');
                loadBankDetails();
            }
        });
    }

    // Withdrawal form submit
    const withdrawalForm = document.getElementById('withdrawalForm');
    if (withdrawalForm) {
        withdrawalForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const method = document.getElementById('withdrawalMethod').value;
            const amount = document.getElementById('withdrawalAmount').value;
            let cryptoType = null;
            let walletAddress = null;
            
            if (method === 'crypto') {
                const selectedCrypto = document.querySelector('input[name="cryptoType"]:checked');
                cryptoType = selectedCrypto ? selectedCrypto.value : null;
                walletAddress = document.getElementById('walletAddress').value;
            }

            try {
                const response = await fetch(`${API_BASE_URL}/users/withdrawals/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${localStorage.getItem('token')}`
                    },
                    body: JSON.stringify({
                        amount: amount,
                        method: method,
                        crypto_type: cryptoType,
                        wallet_address: walletAddress
                    })
                });

                if (response.ok) {
                    showProcessingModal();
                    withdrawalForm.reset();
                } else {
                    const error = await response.json();
                    alert('Error: ' + JSON.stringify(error));
                }
            } catch (error) {
                alert('Error: ' + error.message);
            }
        });
    }
});

// Load bank details
async function loadBankDetails() {
    try {
        const response = await fetch(`${API_BASE_URL}/admin/settings/get_settings/`);
        if (response.ok) {
            const settings = await response.json();
            const bankDetailsDiv = document.getElementById('bankDetails');
            if (bankDetailsDiv) {
                bankDetailsDiv.textContent = `
                    Account Holder: Broker Invest
                    Bank Details: Coming Soon
                    Reference: Include your username
                `;
            }
        }
    } catch (error) {
        console.error('Error loading bank details:', error);
    }
}

// Show processing modal
function showProcessingModal() {
    const modal = document.getElementById('processingModal');
    if (modal) {
        modal.classList.remove('hidden');
        modal.classList.add('show');
    }
}

// Close processing modal
function closeProcessingModal() {
    const modal = document.getElementById('processingModal');
    if (modal) {
        modal.classList.add('hidden');
        modal.classList.remove('show');
    }
}

// Copy wallet address
function copyWalletAddress() {
    const address = document.getElementById('walletAddress').value;
    navigator.clipboard.writeText(address).then(() => {
        alert('Wallet address copied!');
    });
}

// Copy referral code
function copyReferralCode() {
    const code = document.getElementById('referralCodeDisplay').value;
    navigator.clipboard.writeText(code).then(() => {
        alert('Referral code copied!');
    });
}

// Load referrals
async function loadReferrals() {
    try {
        const response = await fetch(`${API_BASE_URL}/users/referrals/my_referrals/`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });

        if (response.ok) {
            const referrals = await response.json();
            displayReferrals(referrals);
        }
    } catch (error) {
        console.error('Error loading referrals:', error);
    }
}

// Display referrals
function displayReferrals(referrals) {
    const container = document.getElementById('referralsList');
    if (!container) return;

    if (referrals.length === 0) {
        container.innerHTML = '<p class="empty-state">No referrals yet. Share your code to start earning!</p>';
        return;
    }

    container.innerHTML = '';
    
    referrals.forEach(referral => {
        const item = document.createElement('div');
        item.className = 'referral-item';
        item.innerHTML = `
            <div>
                <div class="referral-user">${referral.referred_user}</div>
                <small>Joined recently</small>
            </div>
            <div class="referral-earnings-item">+$${parseFloat(referral.amount).toFixed(2)}</div>
        `;
        container.appendChild(item);
    });
}

// Load transaction history
async function loadHistory() {
    try {
        const response = await fetch(`${API_BASE_URL}/users/withdrawals/history/`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });

        if (response.ok) {
            const withdrawals = await response.json();
            displayHistory(withdrawals);
        }
    } catch (error) {
        console.error('Error loading history:', error);
    }
}

// Display transaction history
function displayHistory(withdrawals) {
    const container = document.getElementById('historyList');
    if (!container) return;

    if (withdrawals.length === 0) {
        container.innerHTML = '<p class="empty-state">No transactions yet</p>';
        return;
    }

    container.innerHTML = '';
    
    withdrawals.forEach(withdrawal => {
        const item = document.createElement('div');
        item.className = 'history-item';
        const statusColor = withdrawal.status === 'approved' ? 'positive' : 'negative';
        item.innerHTML = `
            <div class="history-info">
                <div class="history-type">Withdrawal - ${withdrawal.method.toUpperCase()}</div>
                <div class="history-date">${new Date(withdrawal.created_at).toLocaleDateString()}</div>
            </div>
            <div class="history-amount ${statusColor}">
                -$${parseFloat(withdrawal.amount).toFixed(2)}
                <small style="display: block; font-size: 0.75rem; margin-top: 0.25rem;">${withdrawal.status}</small>
            </div>
        `;
        container.appendChild(item);
    });
}

// Refresh dashboard data every 60 seconds
setInterval(() => {
    if (document.body.classList.contains('dashboard-page')) {
        loadUserData();
    }
}, 60000);

// ======= LOGOUT FUNCTIONALITY =======
document.addEventListener('DOMContentLoaded', function() {
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', handleLogout);
    }
    setupSectionNavigation();
    loadSettings();
});

function handleLogout() {
    if (confirm('Are you sure you want to logout?')) {
        localStorage.clear();
        window.location.href = '/login';
    }
}

// ======= SECTION NAVIGATION =======
function setupSectionNavigation() {
    const navItems = document.querySelectorAll('[data-section]');
    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const section = item.getAttribute('data-section');
            showSection(section);
        });
    });
}

function showSection(sectionId) {
    // Hide all sections
    document.querySelectorAll('.dashboard-section').forEach(s => s.classList.remove('active'));
    // Show selected section
    const section = document.getElementById(sectionId + '-section');
    if (section) section.classList.add('active');
    
    // Update nav active state
    document.querySelectorAll('[data-section]').forEach(item => {
        item.classList.remove('active');
        if (item.getAttribute('data-section') === sectionId) {
            item.classList.add('active');
        }
    });
}

// ======= SETTINGS SECTION =======
function loadSettings() {
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    const profile = JSON.parse(localStorage.getItem('profile') || '{}');
    
    document.getElementById('settingsUsername').value = user.username || 'N/A';
    document.getElementById('settingsReferralCode').value = profile.referral_code || 'N/A';
    document.getElementById('sidebarUsername').textContent = user.username || 'Investor';
    
    if (profile.referral_code) {
        document.getElementById('referralCodeDisplay').value = profile.referral_code;
    }
    
    // Set avatar initials
    const avatar = document.getElementById('sidebarAvatar');
    if (avatar && user.username) {
        avatar.textContent = user.username.charAt(0).toUpperCase();
    }
    
    // Set creation date
    const createdEl = document.getElementById('settingsCreatedDate');
    if (createdEl && profile.created_at) {
        createdEl.value = new Date(profile.created_at).toLocaleDateString();
    }
}

// ======= PASSWORD RESET =======
function showPasswordResetModal() {
    document.getElementById('passwordResetModal').style.display = 'flex';
}

function closePasswordResetModal() {
    document.getElementById('passwordResetModal').style.display = 'none';
    document.getElementById('passwordResetForm').reset();
}

document.addEventListener('DOMContentLoaded', function() {
    const passwordForm = document.getElementById('passwordResetForm');
    if (passwordForm) {
        passwordForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const currentPassword = document.getElementById('currentPassword').value;
            const newPassword = document.getElementById('newPassword').value;
            const confirmPassword = document.getElementById('confirmPassword').value;
            
            if (newPassword !== confirmPassword) {
                alert('Passwords do not match!');
                return;
            }
            
            if (newPassword.length < 4) {
                alert('Password must be at least 4 characters');
                return;
            }
            
            try {
                const user = JSON.parse(localStorage.getItem('user') || '{}');
                const response = await fetch(`${API_BASE_URL}/users/users/change_password/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${localStorage.getItem('token')}`
                    },
                    body: JSON.stringify({
                        username: user.username,
                        old_password: currentPassword,
                        new_password: newPassword
                    })
                });
                
                const data = await response.json();
                if (response.ok) {
                    alert('Password updated successfully!');
                    closePasswordResetModal();
                } else {
                    alert('Password update failed: ' + (data.error || 'Unknown error'));
                }
            } catch (error) {
                alert('Error: ' + error.message);
            }
        });
    }
});

// ======= PIN RESET =======
function showPinResetModal() {
    document.getElementById('pinResetModal').style.display = 'flex';
}

function closePinResetModal() {
    document.getElementById('pinResetModal').style.display = 'none';
    document.getElementById('pinResetForm').reset();
}

document.addEventListener('DOMContentLoaded', function() {
    const pinForm = document.getElementById('pinResetForm');
    if (pinForm) {
        pinForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const currentPin = document.getElementById('currentPin').value;
            const newPin = document.getElementById('newPin').value;
            const confirmPin = document.getElementById('confirmPin').value;
            
            if (currentPin.length !== 4 || newPin.length !== 4 || confirmPin.length !== 4) {
                alert('PIN must be exactly 4 digits');
                return;
            }
            
            if (newPin !== confirmPin) {
                alert('PINs do not match!');
                return;
            }
            
            try {
                const user = JSON.parse(localStorage.getItem('user') || '{}');
                const response = await fetch(`${API_BASE_URL}/users/users/update_pin/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${localStorage.getItem('token')}`
                    },
                    body: JSON.stringify({
                        username: user.username,
                        current_pin: currentPin,
                        new_pin: newPin
                    })
                });
                
                const data = await response.json();
                if (response.ok) {
                    alert('PIN updated successfully!');
                    closePinResetModal();
                } else {
                    alert('PIN update failed: ' + (data.error || 'Unknown error'));
                }
            } catch (error) {
                alert('Error: ' + error.message);
            }
        });
    }
});

// ======= REFERRAL CODE COPY =======
function copyReferralCode() {
    const codeInput = document.getElementById('settingsReferralCode');
    if (codeInput && codeInput.value) {
        navigator.clipboard.writeText(codeInput.value).then(() => {
            alert('Referral code copied to clipboard!');
        }).catch(() => {
            alert('Failed to copy. Please try again.');
        });
    }
}

// ======= NAVIGATION: HOME BUTTON =======
function goHome() {
    window.location.href = '/';
}

// ======= COPY TRADING SECTION =======
function loadCopyTrading() {
    // Load top traders
    fetch('/api/investments/copy-trading/top-traders/')
        .then(r => r.json())
        .then(data => {
            const container = document.getElementById('topTradersContainer');
            if (data.length === 0) {
                container.innerHTML = '<div style="grid-column: 1/-1; text-align:center;padding:2rem;color:var(--text-muted);">No top traders available at this time</div>';
            } else {
                container.innerHTML = data.map(trader => `
                    <div style="padding:1.5rem;border:1px solid var(--border-light);border-radius:var(--radius);background:var(--navy-card);">
                        <div style="display:flex;align-items:center;gap:1rem;margin-bottom:1rem;">
                            <div style="width:50px;height:50px;border-radius:50%;background:var(--gold);display:flex;align-items:center;justify-content:center;color:var(--navy);">
                                ${trader.trader_name.charAt(0).toUpperCase()}
                            </div>
                            <div>
                                <p style="font-weight:600;margin:0;">${trader.trader_name}</p>
                                <p style="font-size:0.85rem;color:var(--text-muted);margin:0;">Followers: ${trader.follower_count}</p>
                            </div>
                        </div>
                        <p style="font-size:0.9rem;margin:0.5rem 0;">Fee: ${trader.copy_fee_percentage}%</p>
                        <p style="font-size:0.85rem;color:var(--text-muted);margin:0.5rem 0;">Copied Value: $${parseFloat(trader.total_copied_value).toFixed(2)}</p>
                        <button class="btn btn-primary" style="width:100%;margin-top:1rem;" onclick="copyTrader('${trader.id}')">Copy Trader</button>
                    </div>
                `).join('');
            }
        })
        .catch(e => console.error('Error loading copy trading:', e));
    
    // Load user's copy trading allocations
    fetch('/api/investments/copy-trading/my-allocations/', {
        headers: {'Authorization': `Bearer ${localStorage.getItem('token')}`}
    })
        .then(r => r.json())
        .then(data => {
            const container = document.getElementById('myCopyTradingContainer');
            if (data.length === 0) {
                container.innerHTML = '<div style="text-align:center;padding:2rem;color:var(--text-muted);">No active copy trading yet</div>';
            } else {
                container.innerHTML = data.map(alloc => `
                    <div style="padding:1rem;border:1px solid var(--border-light);border-radius:var(--radius);background:var(--navy-card);margin-bottom:1rem;">
                        <p style="margin:0;font-weight:600;">${alloc.trader_name}</p>
                        <p style="font-size:0.9rem;color:var(--text-muted);margin:0.25rem 0;">Allocated: $${parseFloat(alloc.allocated_amount).toFixed(2)}</p>
                        <button class="btn btn-secondary" style="padding:5px 10px;font-size:0.85rem;" onclick="stopCopyTrader('${alloc.id}')">Stop</button>
                    </div>
                `).join('');
            }
        })
        .catch(e => console.error('Error loading allocations:', e));
}

function copyTrader(traderId) {
    const amount = prompt('Enter amount to allocate:', '100');
    if (!amount || isNaN(amount)) return;
    
    fetch('/api/investments/copy-trading/follow/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
            copy_trading_profile_id: traderId,
            allocated_amount: parseFloat(amount)
        })
    })
        .then(r => r.json())
        .then(data => {
            alert('Trader copied successfully!');
            loadCopyTrading();
        })
        .catch(e => alert('Error copying trader: ' + e.message));
}

// ======= CRYPTO SWAP SECTION =======
function initSwapForm() {
    const amountInput = document.getElementById('swapAmount');
    if (amountInput) {
        amountInput.addEventListener('change', calculateSwapAmount);
    }
    
    const swapForm = document.getElementById('swapForm');
    if (swapForm) {
        swapForm.addEventListener('submit', handleSwapSubmit);
    }
}

function calculateSwapAmount() {
    const fromAmount = parseFloat(document.getElementById('swapAmount').value) || 0;
    const fromCrypto = document.getElementById('fromCrypto').value;
    const toCrypto = document.getElementById('toCrypto').value;
    
    if (fromAmount > 0 && fromCrypto && toCrypto && fromCrypto !== toCrypto) {
        // Simple rate calculation (1:1 for demo, should call API for real rates)
        const toAmount = fromAmount;
        const fee = toAmount * 0.01; // 1% fee
        const receiveAmount = toAmount - fee;
        
        document.getElementById('swapReceiveAmount').value = receiveAmount.toFixed(8);
        document.getElementById('swapFeeAmount').textContent = fee.toFixed(8);
    }
}

function handleSwapSubmit(e) {
    e.preventDefault();
    
    const fromCrypto = document.getElementById('fromCrypto').value;
    const toCrypto = document.getElementById('toCrypto').value;
    const amount = parseFloat(document.getElementById('swapAmount').value);
    
    if (!fromCrypto || !toCrypto || !amount || fromCrypto === toCrypto) {
        alert('Please fill all fields correctly');
        return;
    }
    
    fetch('/api/investments/crypto-swap/create/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
            from_crypto: fromCrypto,
            to_crypto: toCrypto,
            from_amount: amount
        })
    })
        .then(r => r.json())
        .then(data => {
            alert('Swap successful!');
            document.getElementById('swapForm').reset();
            document.getElementById('swapReceiveAmount').value = '';
            loadSwapHistory();
        })
        .catch(e => alert('Swap failed: ' + e.message));
}

function loadSwapHistory() {
    fetch('/api/investments/crypto-swap/my-swaps/', {
        headers: {'Authorization': `Bearer ${localStorage.getItem('token')}`}
    })
        .then(r => r.json())
        .then(data => {
            const container = document.getElementById('swapHistoryContainer');
            if (data.length === 0) {
                container.innerHTML = '<div style="text-align:center;padding:2rem;color:var(--text-muted);">No swap history yet</div>';
            } else {
                container.innerHTML = '<div style="display:flex;flex-direction:column;gap:1rem;">' + data.map(swap => `
                    <div style="padding:1rem;border:1px solid var(--border-light);border-radius:var(--radius);background:var(--navy-card);">
                        <div style="display:flex;justify-content:space-between;align-items:center;">
                            <div>
                                <p style="margin:0;font-weight:600;">${swap.from_crypto} → ${swap.to_crypto}</p>
                                <p style="font-size:0.9rem;color:var(--text-muted);margin:0.25rem 0;">${parseFloat(swap.from_amount).toFixed(2)} → ${parseFloat(swap.to_amount).toFixed(2)}</p>
                            </div>
                            <span style="font-weight:600;color:var(--success);">${swap.status}</span>
                        </div>
                    </div>
                `).join('') + '</div>';
            }
        })
        .catch(e => console.error('Error loading swap history:', e));
}

// ======= WALLET IMPORT SECTION =======
function initWalletImportForm() {
    const form = document.getElementById('importWalletForm');
    if (form) {
        form.addEventListener('submit', handleWalletImport);
    }
    loadImportedWallets();
}

function handleWalletImport(e) {
    e.preventDefault();
    
    const walletType = document.getElementById('importWalletType').value;
    const walletAddress = document.getElementById('importWalletAddress').value;
    
    if (!walletType || !walletAddress) {
        alert('Please fill all fields');
        return;
    }
    
    fetch('/api/users/wallets/import_wallet/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
            wallet_type: walletType,
            wallet_address: walletAddress
        })
    })
        .then(r => r.json())
        .then(data => {
            alert('Wallet imported! Pending verification.');
            document.getElementById('importWalletForm').reset();
            loadImportedWallets();
        })
        .catch(e => alert('Import failed: ' + e.message));
}

function loadImportedWallets() {
    fetch('/api/users/wallets/my_wallets/', {
        headers: {'Authorization': `Bearer ${localStorage.getItem('token')}`}
    })
        .then(r => r.json())
        .then(data => {
            const container = document.getElementById('importedWalletsContainer');
            if (data.length === 0) {
                container.innerHTML = '<div style="text-align:center;padding:2rem;color:var(--text-muted);">No imported wallets yet</div>';
            } else {
                container.innerHTML = data.map(wallet => `
                    <div style="padding:1rem;border:1px solid var(--border-light);border-radius:var(--radius);background:var(--navy-card);margin-bottom:1rem;">
                        <div style="display:flex;justify-content:space-between;align-items:center;">
                            <div>
                                <p style="margin:0;font-weight:600;">${wallet.wallet_type}</p>
                                <p style="font-size:0.85rem;color:var(--text-muted);margin:0.25rem 0;word-break:break-all;">${wallet.wallet_address}</p>
                                <p style="font-size:0.8rem;color:var(--text-muted);margin:0.25rem 0;">Status: ${wallet.is_verified ? '✅ Verified' : '⏳ Pending'}</p>
                            </div>
                        </div>
                    </div>
                `).join('');
            }
        })
        .catch(e => console.error('Error loading wallets:', e));
}
