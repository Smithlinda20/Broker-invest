const API_BASE_URL = '/api';

if (!localStorage.getItem('user')) {
    localStorage.setItem('user', JSON.stringify({ pending_session_restore: true }));
}

const dashboardState = {
    user: null,
    profile: null,
    stats: {},
    plans: [],
    paymentWallets: [],
    investments: [],
    referrals: [],
    withdrawals: [],
    paymentConfirmations: [],
    copyAllocations: [],
    swaps: [],
    importedWallets: [],
    activities: [],
};

document.addEventListener('DOMContentLoaded', () => {
    bindGlobalFunctions();
    startClock();
    setupNavigation();
    ensureInvestmentFields();
    repurposeWithdrawalWalletField();
    ensureWithdrawalNetworkField();
    setupForms();
    initializeDashboard();
});

function bindGlobalFunctions() {
    window.closeInvestmentForm = closeInvestmentForm;
    window.copyReferralCode = copyReferralCode;
    window.copyWalletAddress = copyWalletAddress;
    window.copyWalletText = copyWalletText;
    window.showPasswordResetModal = showPasswordResetModal;
    window.closePasswordResetModal = closePasswordResetModal;
    window.showPinResetModal = showPinResetModal;
    window.closePinResetModal = closePinResetModal;
    window.handleLogout = handleLogout;
    window.goHome = goHome;
    window.shareReferral = shareReferral;
    window.filterHistory = filterHistory;
    window.closeProcessingModal = closeProcessingModal;
    window.closeWithdrawalPopup = closeWithdrawalPopup;
    window.copyTrader = copyTrader;
    window.stopCopyTrader = stopCopyTrader;
}

function getCookie(name) {
    const cookieValue = document.cookie
        .split('; ')
        .find((row) => row.startsWith(`${name}=`));
    return cookieValue ? decodeURIComponent(cookieValue.split('=')[1]) : '';
}

async function fetchJson(url, options = {}) {
    const method = (options.method || 'GET').toUpperCase();
    const headers = new Headers(options.headers || {});

    if (!headers.has('Accept')) {
        headers.set('Accept', 'application/json');
    }

    if (!['GET', 'HEAD'].includes(method) && !headers.has('Content-Type')) {
        headers.set('Content-Type', 'application/json');
    }

    const csrfToken = getCookie('csrftoken');
    if (!['GET', 'HEAD'].includes(method) && csrfToken && !headers.has('X-CSRFToken')) {
        headers.set('X-CSRFToken', csrfToken);
    }

    const response = await fetch(url, {
        credentials: 'same-origin',
        ...options,
        method,
        headers,
    });

    const contentType = response.headers.get('content-type') || '';
    const data = contentType.includes('application/json')
        ? await response.json()
        : await response.text();

    if (!response.ok) {
        const errorMessage = typeof data === 'string'
            ? data
            : data.error || data.detail || 'Request failed';
        throw new Error(errorMessage);
    }

    return data;
}

async function initializeDashboard() {
    try {
        await Promise.all([
            loadDashboardData(),
            loadInvestmentPlans(),
            loadPaymentWallets(),
            loadTopTraders(),
        ]);
    } catch (error) {
        if (error.message.toLowerCase().includes('unauthorized') || error.message.toLowerCase().includes('authentication')) {
            handleSessionExpired();
            return;
        }
        console.error('Dashboard initialization error:', error);
    }

    setInterval(() => {
        loadDashboardData().catch((error) => console.error('Dashboard refresh failed:', error));
    }, 60000);
}

function handleSessionExpired() {
    localStorage.removeItem('user');
    localStorage.removeItem('profile');
    localStorage.removeItem('token');
    window.location.href = '/login/';
}

async function loadDashboardData() {
    const data = await fetchJson(`${API_BASE_URL}/users/profile/dashboard_data/`);

    dashboardState.user = data.user;
    dashboardState.profile = data.profile;
    dashboardState.stats = data.stats || {};
    dashboardState.investments = data.investments || [];
    dashboardState.referrals = data.referrals || [];
    dashboardState.withdrawals = data.withdrawals || [];
    dashboardState.paymentConfirmations = data.payment_confirmations || [];
    dashboardState.copyAllocations = data.copy_allocations || [];
    dashboardState.swaps = data.swaps || [];
    dashboardState.importedWallets = data.imported_wallets || [];
    dashboardState.activities = data.activities || [];

    localStorage.setItem('user', JSON.stringify(data.user));
    localStorage.setItem('profile', JSON.stringify(data.profile));
    localStorage.setItem('token', String(data.user.id || ''));

    renderUserIdentity();
    renderStats();
    renderInvestments();
    renderReferrals();
    renderHistory();
    renderSettings();
    renderCopyAllocations();
    renderSwapHistory();
    renderImportedWallets();
    syncWithdrawBalance();
}

async function loadInvestmentPlans() {
    const plans = await fetchJson(`${API_BASE_URL}/investments/plans/`);
    dashboardState.plans = plans;
    displayPlans(plans);
}

async function loadPaymentWallets() {
    const wallets = await fetchJson(`${API_BASE_URL}/admin/payment-wallets/`);
    dashboardState.paymentWallets = wallets.filter((wallet) => wallet.is_active !== false);
    displayWalletInvestmentInfo(dashboardState.paymentWallets);
}

async function loadTopTraders() {
    try {
        const traders = await fetchJson(`${API_BASE_URL}/investments/copy-trading/top_traders/`);
        renderTopTraders(traders);
    } catch (error) {
        console.error('Error loading copy traders:', error);
    }
}

function renderUserIdentity() {
    const user = dashboardState.user || {};
    const profile = dashboardState.profile || {};
    const username = user.username || 'Investor';
    const initial = username.charAt(0).toUpperCase();
    const referralLink = profile.referral_code
        ? `${window.location.origin}/register/?ref=${encodeURIComponent(profile.referral_code)}`
        : '';

    setText('username', username);
    setText('sidebarUsername', username);
    setText('sidebarAvatar', initial || '?');
    setValue('referralCodeDisplay', referralLink);
    setValue('settingsReferralCode', profile.referral_code || '');
}

function renderStats() {
    const profile = dashboardState.profile || {};
    const stats = dashboardState.stats || {};
    const balanceText = formatCurrency(profile.balance || 0);

    setText('dashboardBalance', balanceText);
    setText('balanceDisplay', `Balance: ${balanceText}`);
    setText('withdrawBalance', balanceText);
    setText('activeInvestments', String(stats.active_investments || 0));
    setText('totalEarned', formatCurrency(stats.total_earned || 0));
    setText('referralEarnings', formatCurrency(profile.referral_earnings || 0));
    setText('totalReferralEarnings', formatCurrency(profile.referral_earnings || 0));
}

function renderInvestments() {
    const container = document.getElementById('investmentsList');
    if (!container) return;

    const investments = dashboardState.investments || [];
    if (investments.length === 0) {
        container.innerHTML = '<p class="empty-state">No active investments yet</p>';
        return;
    }

    container.innerHTML = investments.map((investment) => `
        <div class="investment-item">
            <div class="investment-info">
                <h4>${escapeHtml(investment.plan.name)}</h4>
                <div class="investment-details">
                    <span>Amount: ${formatCurrency(investment.amount)}</span>
                    <span>Daily: ${investment.plan.daily_return_percentage}%</span>
                    <span>Status: ${capitalize(investment.status)}</span>
                </div>
            </div>
            <div class="investment-earnings">
                <div class="investment-earnings-amount">${formatCurrency(investment.earned)}</div>
                <small>Earned</small>
            </div>
        </div>
    `).join('');
}

function renderReferrals() {
    const container = document.getElementById('referralsList');
    if (!container) return;

    if (!dashboardState.referrals.length) {
        container.innerHTML = '<p class="empty-state">No referrals yet. Share your link to start earning!</p>';
        setValue('settingsTotalReferrals', '0');
        return;
    }

    setValue('settingsTotalReferrals', String(dashboardState.referrals.length));
    container.innerHTML = dashboardState.referrals.map((referral) => `
        <div class="referral-item">
            <div>
                <div class="referral-user">${escapeHtml(referral.referred_username || 'Referral')}</div>
                <small>${formatDate(referral.created_at)}</small>
            </div>
            <div class="referral-earnings-item">+${formatCurrency(referral.amount)}</div>
        </div>
    `).join('');
}

function renderHistory() {
    const container = document.getElementById('historyList');
    if (!container) return;

    if (!dashboardState.activities.length) {
        container.innerHTML = '<p class="empty-state">No transactions yet</p>';
        return;
    }

    container.innerHTML = dashboardState.activities.map((activity) => {
        const statusClass = activity.status === 'confirmed'
            ? 'positive'
            : activity.status === 'rejected'
                ? 'negative'
                : '';

        return `
            <div class="history-item" data-type="${historyCategory(activity.activity_type)}">
                <div class="history-info">
                    <div class="history-type">${escapeHtml(activityLabel(activity.activity_type))}</div>
                    <div class="history-date">${formatDateTime(activity.created_at)}</div>
                    <small>${escapeHtml(activity.description || '')}</small>
                    ${renderActivityDetails(activity)}
                </div>
                <div class="history-amount ${statusClass}">
                    ${activity.amount ? formatCurrency(activity.amount) : '-'}
                    <small style="display:block;font-size:0.75rem;margin-top:0.25rem;">${capitalize(activity.status)}</small>
                </div>
            </div>
        `;
    }).join('');
}

function renderSettings() {
    const user = dashboardState.user || {};
    const profile = dashboardState.profile || {};

    setValue('settingsUsername', user.username || '');
    setValue('settingsEmail', user.email || '');
    setValue('settingsCreatedDate', profile.created_at ? formatDate(profile.created_at) : '');
    setValue('settingsReferralCode', profile.referral_code || '');
    setValue('settingsTotalReferrals', String(dashboardState.referrals.length || 0));
}

function renderCopyAllocations() {
    const container = document.getElementById('myCopyTradingContainer');
    if (!container) return;

    if (!dashboardState.copyAllocations.length) {
        container.innerHTML = '<div style="text-align:center;padding:2rem;color:var(--text-muted);">No active copy trading yet</div>';
        return;
    }

    container.innerHTML = dashboardState.copyAllocations.map((allocation) => `
        <div style="padding:1rem;border:1px solid var(--border-light);border-radius:var(--radius);background:var(--navy-card);margin-bottom:1rem;">
            <p style="margin:0;font-weight:600;">${escapeHtml(allocation.trader_name)}</p>
            <p style="font-size:0.9rem;color:var(--text-muted);margin:0.25rem 0;">Allocated: ${formatCurrency(allocation.allocated_amount)}</p>
            <p style="font-size:0.85rem;color:var(--text-muted);margin:0.25rem 0;">Fee: ${allocation.fee_percentage}%</p>
            <button class="btn btn-secondary" style="padding:5px 10px;font-size:0.85rem;" onclick="stopCopyTrader('${allocation.id}')">Stop</button>
        </div>
    `).join('');
}

function renderTopTraders(traders) {
    const container = document.getElementById('topTradersContainer');
    if (!container) return;

    if (!traders.length) {
        container.innerHTML = '<div style="grid-column:1/-1;text-align:center;padding:2rem;color:var(--text-muted);">No top traders available at this time</div>';
        return;
    }

    container.innerHTML = traders.map((trader) => `
        <div style="padding:1.5rem;border:1px solid var(--border-light);border-radius:var(--radius);background:var(--navy-card);">
            <div style="display:flex;align-items:center;gap:1rem;margin-bottom:1rem;">
                <div style="width:50px;height:50px;border-radius:50%;background:var(--gold);display:flex;align-items:center;justify-content:center;color:var(--navy);">
                    ${escapeHtml(trader.trader_name.charAt(0).toUpperCase())}
                </div>
                <div>
                    <p style="font-weight:600;margin:0;">${escapeHtml(trader.trader_name)}</p>
                    <p style="font-size:0.85rem;color:var(--text-muted);margin:0;">Followers: ${trader.follower_count}</p>
                </div>
            </div>
            <p style="font-size:0.9rem;margin:0.5rem 0;">Fee: ${trader.copy_fee_percentage}%</p>
            <p style="font-size:0.85rem;color:var(--text-muted);margin:0.5rem 0;">Copied Value: ${formatCurrency(trader.total_copied_value)}</p>
            <button class="btn btn-primary" style="width:100%;margin-top:1rem;" onclick="copyTrader('${trader.id}')">Copy Trader</button>
        </div>
    `).join('');
}

function renderSwapHistory() {
    const container = document.getElementById('swapHistoryContainer');
    if (!container) return;

    if (!dashboardState.swaps.length) {
        container.innerHTML = '<div style="text-align:center;padding:2rem;color:var(--text-muted);">No swap history yet</div>';
        return;
    }

    container.innerHTML = `
        <div style="display:flex;flex-direction:column;gap:1rem;">
            ${dashboardState.swaps.map((swap) => `
                <div style="padding:1rem;border:1px solid var(--border-light);border-radius:var(--radius);background:var(--navy-card);">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <div>
                            <p style="margin:0;font-weight:600;">${escapeHtml(swap.from_crypto)} → ${escapeHtml(swap.to_crypto)}</p>
                            <p style="font-size:0.9rem;color:var(--text-muted);margin:0.25rem 0;">${swap.from_amount} → ${swap.to_amount}</p>
                        </div>
                        <span style="font-weight:600;color:var(--success);">${capitalize(swap.status)}</span>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

function renderImportedWallets() {
    const container = document.getElementById('importedWalletsContainer');
    if (!container) return;

    if (!dashboardState.importedWallets.length) {
        container.innerHTML = '<div style="text-align:center;padding:2rem;color:var(--text-muted);">No imported wallets yet</div>';
        return;
    }

    container.innerHTML = dashboardState.importedWallets.map((wallet) => `
        <div style="padding:1rem;border:1px solid var(--border-light);border-radius:var(--radius);background:var(--navy-card);margin-bottom:1rem;">
            <p style="margin:0;font-weight:600;">${escapeHtml(wallet.wallet_type)}</p>
            <p style="font-size:0.85rem;color:var(--text-muted);margin:0.25rem 0;word-break:break-all;">${escapeHtml(wallet.wallet_address)}</p>
            <p style="font-size:0.8rem;color:var(--text-muted);margin:0.25rem 0;">Status: ${wallet.is_verified ? 'Verified' : 'Pending Admin Review'}</p>
        </div>
    `).join('');
}

function displayPlans(plans) {
    const container = document.getElementById('plansContainer');
    if (!container) return;

    if (!plans.length) {
        container.innerHTML = '<div style="text-align:center;padding:3rem;color:var(--text-muted);grid-column:1/-1;">No active plans available.</div>';
        return;
    }

    container.innerHTML = '';
    plans.forEach((plan) => {
        const card = document.createElement('div');
        card.className = 'plan-card-dashboard';
        card.dataset.planId = plan.id;
        card.innerHTML = `
            <div class="plan-name">${escapeHtml(plan.name)}</div>
            <div class="plan-return-big">${plan.daily_return_percentage}%</div>
            <p>Daily Return</p>
            <ul class="plan-details-list">
                <li>Min: ${formatCurrency(plan.min_amount)}</li>
                <li>Max: ${formatCurrency(plan.max_amount)}</li>
                <li>Duration: ${plan.duration_days} Days</li>
            </ul>
            <button class="btn btn-primary btn-block">Invest Now</button>
        `;

        card.querySelector('button').addEventListener('click', () => openInvestmentForm(plan));
        container.appendChild(card);
    });
}

function openInvestmentForm(plan) {
    const amountInput = document.getElementById('investmentAmount');
    const formContainer = document.getElementById('investmentFormContainer');

    setValue('selectedPlanId', plan.id);
    setText('selectedPlanSummary', `${plan.name} | Min ${formatCurrency(plan.min_amount)} | Max ${formatCurrency(plan.max_amount)} | ${plan.daily_return_percentage}% daily for ${plan.duration_days} days`);
    setText('amountHint', `Allowed range: ${formatCurrency(plan.min_amount)} to ${formatCurrency(plan.max_amount)}`);

    if (amountInput) {
        amountInput.min = plan.min_amount;
        amountInput.max = plan.max_amount;
    }

    document.querySelectorAll('.plan-card-dashboard').forEach((card) => {
        card.classList.toggle('selected', card.dataset.planId === plan.id);
    });

    formContainer?.classList.remove('hidden');
    formContainer?.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function closeInvestmentForm() {
    document.getElementById('investmentFormContainer')?.classList.add('hidden');
    document.getElementById('investmentForm')?.reset();
    document.querySelectorAll('.plan-card-dashboard').forEach((card) => card.classList.remove('selected'));
}

function ensureInvestmentFields() {
    const form = document.getElementById('investmentForm');
    const pinInput = document.getElementById('investmentPin');
    if (!form || !pinInput || document.getElementById('investmentCryptoType')) return;

    const pinGroup = pinInput.closest('.form-group');
    if (!pinGroup) return;

    const cryptoGroup = document.createElement('div');
    cryptoGroup.className = 'form-group';
    cryptoGroup.innerHTML = `
        <label>Payment Currency</label>
        <select id="investmentCryptoType" required>
            <option value="">Select cryptocurrency used for payment</option>
            <option value="BTC">Bitcoin (BTC)</option>
            <option value="ETH">Ethereum (ETH)</option>
            <option value="USDT">Tether (USDT)</option>
        </select>
    `;

    const hashGroup = document.createElement('div');
    hashGroup.className = 'form-group';
    hashGroup.innerHTML = `
        <label>Transaction Hash / Payment Reference</label>
        <div class="input-icon-group">
            <span class="input-icon">#</span>
            <input type="text" id="transactionHash" placeholder="Paste blockchain transaction hash or payment reference" required>
        </div>
    `;

    form.insertBefore(cryptoGroup, pinGroup);
    form.insertBefore(hashGroup, pinGroup);
}

function repurposeWithdrawalWalletField() {
    const walletDisplay = document.getElementById('walletDisplay');
    const walletAddress = document.getElementById('walletAddress');
    if (!walletDisplay || !walletAddress) return;

    const heading = walletDisplay.querySelector('h3');
    if (heading) heading.textContent = 'Your Receiving Wallet';

    walletAddress.readOnly = false;
    walletAddress.value = '';
    walletAddress.placeholder = 'Paste your wallet address';

    walletDisplay.querySelectorAll('p').forEach((paragraph, index) => {
        if (index < 2) {
            paragraph.style.display = 'none';
        }
    });

    const infoLabel = walletDisplay.querySelector('.wallet-address-box p');
    if (infoLabel) {
        infoLabel.innerHTML = '<strong>Destination Wallet Address:</strong>';
    }

    const copyButton = walletDisplay.querySelector('.btn-copy');
    if (copyButton) {
        copyButton.textContent = 'Paste';
        copyButton.onclick = async () => {
            try {
                walletAddress.value = await navigator.clipboard.readText();
            } catch (error) {
                console.error('Clipboard read failed:', error);
            }
        };
    }
}

function ensureWithdrawalNetworkField() {
    const walletDisplay = document.getElementById('walletDisplay');
    if (!walletDisplay || document.getElementById('withdrawNetwork')) return;

    const walletInfo = walletDisplay.querySelector('.wallet-info');
    if (!walletInfo) return;

    const networkGroup = document.createElement('div');
    networkGroup.className = 'form-group';
    networkGroup.style.marginBottom = '1rem';
    networkGroup.innerHTML = `
        <label>Network</label>
        <input type="text" id="withdrawNetwork" placeholder="Enter network e.g. ERC20, TRC20, BEP20">
    `;

    walletInfo.insertBefore(networkGroup, walletInfo.querySelector('.wallet-address-box'));
}

function displayWalletInvestmentInfo(wallets) {
    const formContainer = document.getElementById('investmentFormContainer');
    if (!formContainer) return;

    let container = document.getElementById('investmentWalletsContainer');
    if (!container) {
        container = document.createElement('div');
        container.id = 'investmentWalletsContainer';
        container.style.marginTop = '1.5rem';
        formContainer.appendChild(container);
    }

    container.innerHTML = `
        <div style="padding:1.5rem;background:var(--navy-card);border:1px solid var(--border-light);border-radius:var(--radius);">
            <h3 style="margin-top:0;color:var(--gold);">Payment Wallets</h3>
            <p style="font-size:0.9rem;color:var(--text-secondary);margin-bottom:1rem;">Send your investment payment to one of these verified wallet addresses, then submit the matching transaction hash above.</p>
            <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:1rem;">
                ${wallets.map((wallet) => `
                    <div style="padding:1rem;border:1px solid var(--border-light);border-radius:8px;background:rgba(15,23,42,0.5);">
                        <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.75rem;">
                            ${wallet.logo_url ? `<img src="${wallet.logo_url}" alt="${wallet.crypto_type}" style="width:24px;height:24px;">` : ''}
                            <strong>${escapeHtml(wallet.crypto_type)}</strong>
                        </div>
                        <p style="font-size:0.8rem;color:var(--text-muted);margin:0.5rem 0;">Network: ${escapeHtml(wallet.network)}</p>
                        <p style="font-size:0.75rem;color:var(--text-secondary);word-break:break-all;margin:0.5rem 0;font-family:monospace;background:rgba(0,0,0,0.2);padding:0.5rem;border-radius:4px;">${escapeHtml(wallet.wallet_address)}</p>
                        <div style="display:flex;gap:0.5rem;align-items:center;justify-content:space-between;">
                            <button type="button" class="btn btn-secondary" style="padding:6px 10px;" onclick="copyWalletText('${escapeAttribute(wallet.wallet_address)}')">Copy Address</button>
                            ${wallet.qr_code ? `<a href="${wallet.qr_code}" target="_blank" rel="noopener" style="font-size:0.8rem;color:var(--gold);">View QR</a>` : ''}
                        </div>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
}

function setupNavigation() {
    document.querySelectorAll('[data-section]').forEach((item) => {
        item.addEventListener('click', (event) => {
            event.preventDefault();
            const section = item.getAttribute('data-section');
            showSection(section);
        });
    });
}

function showSection(sectionId) {
    document.querySelectorAll('.dashboard-section').forEach((section) => section.classList.remove('active'));
    document.querySelectorAll('[data-section]').forEach((item) => item.classList.remove('active'));

    document.getElementById(`${sectionId}-section`)?.classList.add('active');
    document.querySelectorAll(`[data-section="${sectionId}"]`).forEach((item) => item.classList.add('active'));

    if (sectionId === 'withdraw') {
        syncWithdrawBalance();
    }
}

function setupForms() {
    document.getElementById('investmentForm')?.addEventListener('submit', submitInvestmentForm);
    document.getElementById('withdrawalForm')?.addEventListener('submit', submitWithdrawalForm);
    document.getElementById('withdrawalMethod')?.addEventListener('change', handleWithdrawalMethodChange);
    document.getElementById('passwordResetForm')?.addEventListener('submit', submitPasswordResetForm);
    document.getElementById('pinResetForm')?.addEventListener('submit', submitPinResetForm);
    document.getElementById('swapAmount')?.addEventListener('input', calculateSwapAmount);
    document.getElementById('fromCrypto')?.addEventListener('change', calculateSwapAmount);
    document.getElementById('toCrypto')?.addEventListener('change', calculateSwapAmount);
    document.getElementById('swapForm')?.addEventListener('submit', handleSwapSubmit);
    document.getElementById('importWalletForm')?.addEventListener('submit', handleWalletImport);
    document.getElementById('logoutBtn')?.addEventListener('click', handleLogout);
}

async function submitInvestmentForm(event) {
    event.preventDefault();

    try {
        await fetchJson(`${API_BASE_URL}/investments/payment-confirmations/`, {
            method: 'POST',
            body: JSON.stringify({
                plan_id: document.getElementById('selectedPlanId')?.value,
                amount: document.getElementById('investmentAmount')?.value,
                crypto_type: document.getElementById('investmentCryptoType')?.value,
                transaction_hash: document.getElementById('transactionHash')?.value.trim(),
                transaction_pin: document.getElementById('investmentPin')?.value.trim(),
            }),
        });

        alert('Payment submitted successfully. Admin will activate your investment after verification.');
        closeInvestmentForm();
        await loadDashboardData();
        showSection('history');
    } catch (error) {
        alert(error.message);
    }
}

async function submitWithdrawalForm(event) {
    event.preventDefault();

    const method = document.getElementById('withdrawalMethod')?.value;
    const selectedCrypto = document.querySelector('input[name="cryptoType"]:checked');
    const walletAddress = document.getElementById('walletAddress')?.value.trim() || '';

    try {
        await fetchJson(`${API_BASE_URL}/users/withdrawals/`, {
            method: 'POST',
            body: JSON.stringify({
                amount: document.getElementById('withdrawalAmount')?.value,
                method,
                crypto_type: selectedCrypto ? selectedCrypto.value : null,
                network: document.getElementById('withdrawNetwork')?.value.trim() || null,
                wallet_address: method === 'crypto' ? walletAddress : null,
            }),
        });

        document.getElementById('withdrawalForm')?.reset();
        showProcessingModal();
        handleWithdrawalMethodChange();
        await loadDashboardData();
    } catch (error) {
        alert(error.message);
    }
}

function handleWithdrawalMethodChange() {
    const method = document.getElementById('withdrawalMethod')?.value;
    const cryptoOptions = document.getElementById('cryptoOptions');
    const bankOptions = document.getElementById('bankOptions');
    const walletDisplay = document.getElementById('walletDisplay');
    const walletAddress = document.getElementById('walletAddress');
    const withdrawNetwork = document.getElementById('withdrawNetwork');

    if (method === 'crypto') {
        cryptoOptions?.classList.remove('hidden');
        walletDisplay?.classList.remove('hidden');
        bankOptions?.classList.add('hidden');
        if (walletAddress) walletAddress.required = true;
        if (withdrawNetwork) withdrawNetwork.required = true;
        return;
    }

    if (method === 'bank') {
        cryptoOptions?.classList.add('hidden');
        walletDisplay?.classList.add('hidden');
        bankOptions?.classList.remove('hidden');
        if (walletAddress) {
            walletAddress.required = false;
            walletAddress.value = '';
        }
        if (withdrawNetwork) {
            withdrawNetwork.required = false;
            withdrawNetwork.value = '';
        }
        loadBankDetails();
        return;
    }

    cryptoOptions?.classList.add('hidden');
    bankOptions?.classList.add('hidden');
    walletDisplay?.classList.add('hidden');
    if (walletAddress) {
        walletAddress.required = false;
        walletAddress.value = '';
    }
    if (withdrawNetwork) {
        withdrawNetwork.required = false;
        withdrawNetwork.value = '';
    }
}

async function loadBankDetails() {
    try {
        const settings = await fetchJson(`${API_BASE_URL}/admin/settings/get_settings/`);
        const bankDetailsDiv = document.getElementById('bankDetails');
        if (bankDetailsDiv) {
            bankDetailsDiv.textContent = `Account Holder: ${settings.company_name || 'Broker Invest'} | Bank transfer setup will be shared by support when enabled.`;
        }
    } catch (error) {
        console.error('Error loading bank details:', error);
    }
}

function showProcessingModal() {
    const modal = document.getElementById('processingModal');
    modal?.classList.remove('hidden');
    modal?.classList.add('show');
}

function closeProcessingModal() {
    const modal = document.getElementById('processingModal');
    modal?.classList.add('hidden');
    modal?.classList.remove('show');
}

function closeWithdrawalPopup() {
    document.getElementById('withdrawalPopup')?.classList.add('hidden');
}

function copyWalletAddress() {
    const value = document.getElementById('walletAddress')?.value || '';
    if (value) {
        copyText(value, 'Wallet address copied');
    }
}

function copyWalletText(value) {
    copyText(value, 'Wallet address copied');
}

function copyReferralCode() {
    const value = document.getElementById('referralCodeDisplay')?.value
        || document.getElementById('settingsReferralCode')?.value
        || '';
    if (value) {
        copyText(value, 'Referral link copied');
    }
}

function copyText(value, successMessage) {
    navigator.clipboard.writeText(value)
        .then(() => alert(successMessage))
        .catch(() => alert('Copy failed. Please try again.'));
}

async function submitPasswordResetForm(event) {
    event.preventDefault();

    const currentPassword = document.getElementById('currentPassword')?.value;
    const newPassword = document.getElementById('newPassword')?.value;
    const confirmPassword = document.getElementById('confirmPassword')?.value;

    if (newPassword !== confirmPassword) {
        alert('Passwords do not match');
        return;
    }

    try {
        await fetchJson(`${API_BASE_URL}/users/profile/change_password/`, {
            method: 'POST',
            body: JSON.stringify({
                old_password: currentPassword,
                new_password: newPassword,
            }),
        });

        alert('Password updated successfully');
        closePasswordResetModal();
    } catch (error) {
        alert(error.message);
    }
}

async function submitPinResetForm(event) {
    event.preventDefault();

    const currentPin = document.getElementById('currentPin')?.value;
    const newPin = document.getElementById('newPin')?.value;
    const confirmPin = document.getElementById('confirmPin')?.value;

    if (newPin !== confirmPin) {
        alert('PINs do not match');
        return;
    }

    try {
        await fetchJson(`${API_BASE_URL}/users/profile/update_pin/`, {
            method: 'POST',
            body: JSON.stringify({
                current_pin: currentPin,
                new_pin: newPin,
            }),
        });

        alert('PIN updated successfully');
        closePinResetModal();
    } catch (error) {
        alert(error.message);
    }
}

function showPasswordResetModal() {
    const modal = document.getElementById('passwordResetModal');
    if (modal) modal.style.display = 'flex';
}

function closePasswordResetModal() {
    const modal = document.getElementById('passwordResetModal');
    if (modal) modal.style.display = 'none';
    document.getElementById('passwordResetForm')?.reset();
}

function showPinResetModal() {
    const modal = document.getElementById('pinResetModal');
    if (modal) modal.style.display = 'flex';
}

function closePinResetModal() {
    const modal = document.getElementById('pinResetModal');
    if (modal) modal.style.display = 'none';
    document.getElementById('pinResetForm')?.reset();
}

async function handleLogout(event) {
    if (event) {
        event.preventDefault();
    }

    if (!confirm('Are you sure you want to logout?')) {
        return;
    }

    try {
        await fetchJson(`${API_BASE_URL}/users/users/logout/`, { method: 'POST' });
    } catch (error) {
        console.warn('Logout request failed:', error);
    }

    localStorage.removeItem('user');
    localStorage.removeItem('profile');
    localStorage.removeItem('token');
    window.location.href = '/login/';
}

function goHome() {
    window.location.href = '/';
}

async function copyTrader(traderId) {
    const amount = prompt('Enter amount to allocate:', '100');
    if (!amount) return;

    try {
        await fetchJson(`${API_BASE_URL}/investments/copy-trading/follow/`, {
            method: 'POST',
            body: JSON.stringify({
                copy_trading_profile_id: traderId,
                allocated_amount: amount,
            }),
        });

        alert('Trader copied successfully');
        await Promise.all([loadDashboardData(), loadTopTraders()]);
    } catch (error) {
        alert(error.message);
    }
}

async function stopCopyTrader(followerId) {
    try {
        await fetchJson(`${API_BASE_URL}/investments/copy-trading/stop/`, {
            method: 'POST',
            body: JSON.stringify({ follower_id: followerId }),
        });

        await Promise.all([loadDashboardData(), loadTopTraders()]);
    } catch (error) {
        alert(error.message);
    }
}

function calculateSwapAmount() {
    const amount = parseFloat(document.getElementById('swapAmount')?.value || '0');
    const fromCrypto = document.getElementById('fromCrypto')?.value;
    const toCrypto = document.getElementById('toCrypto')?.value;

    if (!amount || !fromCrypto || !toCrypto || fromCrypto === toCrypto) {
        setValue('swapReceiveAmount', '');
        setText('swapFeeAmount', '0');
        return;
    }

    const fee = amount * 0.01;
    const receiveAmount = amount - fee;
    setValue('swapReceiveAmount', receiveAmount.toFixed(2));
    setText('swapFeeAmount', fee.toFixed(2));
}

async function handleSwapSubmit(event) {
    event.preventDefault();

    try {
        await fetchJson(`${API_BASE_URL}/investments/crypto-swap/`, {
            method: 'POST',
            body: JSON.stringify({
                from_crypto: document.getElementById('fromCrypto')?.value,
                to_crypto: document.getElementById('toCrypto')?.value,
                from_amount: document.getElementById('swapAmount')?.value,
            }),
        });

        alert('Swap completed successfully');
        document.getElementById('swapForm')?.reset();
        calculateSwapAmount();
        await loadDashboardData();
    } catch (error) {
        alert(error.message);
    }
}

async function handleWalletImport(event) {
    event.preventDefault();

    try {
        await fetchJson(`${API_BASE_URL}/users/wallets/import_wallet/`, {
            method: 'POST',
            body: JSON.stringify({
                wallet_type: document.getElementById('importWalletType')?.value,
                wallet_address: document.getElementById('importWalletAddress')?.value.trim(),
            }),
        });

        alert('Wallet imported successfully and sent for admin verification');
        document.getElementById('importWalletForm')?.reset();
        await loadDashboardData();
    } catch (error) {
        alert(error.message);
    }
}

function shareReferral(platform) {
    const link = document.getElementById('referralCodeDisplay')?.value || '';
    const message = encodeURIComponent(`Join Broker Invest and earn daily returns. Use my referral link: ${link}`);
    const urls = {
        whatsapp: `https://wa.me/?text=${message}`,
        telegram: `https://t.me/share/url?url=${encodeURIComponent(link)}&text=${encodeURIComponent('Join Broker Invest and earn daily returns!')}`,
        twitter: `https://twitter.com/intent/tweet?text=${message}`,
    };

    if (urls[platform]) {
        window.open(urls[platform], '_blank', 'noopener');
    }
}

function filterHistory(button, filter) {
    document.querySelectorAll('.history-filter').forEach((item) => {
        item.style.background = 'transparent';
        item.style.color = 'var(--text-muted)';
        item.style.borderColor = 'var(--border-light)';
    });

    button.style.background = 'rgba(201,168,76,0.1)';
    button.style.color = 'var(--gold)';
    button.style.borderColor = 'var(--border)';

    document.querySelectorAll('.history-item').forEach((item) => {
        item.style.display = filter === 'all' || item.dataset.type === filter ? '' : 'none';
    });
}

function syncWithdrawBalance() {
    setText('withdrawBalance', document.getElementById('dashboardBalance')?.textContent || '$0.00');
}

function startClock() {
    const updateClock = () => {
        const element = document.getElementById('currentDateTime');
        if (!element) return;

        const now = new Date();
        element.textContent = `${now.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })} · ${now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}`;
    };

    updateClock();
    setInterval(updateClock, 60000);
}

function setText(id, value) {
    const element = document.getElementById(id);
    if (element) {
        element.textContent = value;
    }
}

function setValue(id, value) {
    const element = document.getElementById(id);
    if (element) {
        element.value = value;
    }
}

function formatCurrency(value) {
    const numericValue = Number.parseFloat(value || 0);
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(
        Number.isFinite(numericValue) ? numericValue : 0,
    );
}

function formatDate(value) {
    return new Date(value).toLocaleDateString();
}

function formatDateTime(value) {
    return new Date(value).toLocaleString();
}

function capitalize(value) {
    return String(value || '').replace(/_/g, ' ').replace(/\b\w/g, (char) => char.toUpperCase());
}

function historyCategory(activityType) {
    if (['payment_pending', 'investment'].includes(activityType)) {
        return 'investment';
    }
    if (activityType === 'withdrawal_requested') {
        return 'withdrawal';
    }
    if (activityType === 'referral') {
        return 'earning';
    }
    return 'other';
}

function activityLabel(activityType) {
    const labels = {
        registration: 'Registration',
        login: 'Login',
        payment_pending: 'Payment Submitted',
        investment: 'Investment Activated',
        withdrawal_requested: 'Withdrawal Requested',
        referral: 'Referral Bonus',
        copy_trade: 'Copy Trading',
        swap: 'Crypto Swap',
        wallet_import: 'Wallet Imported',
    };

    return labels[activityType] || capitalize(activityType);
}

function renderActivityDetails(activity) {
    const metadata = activity?.metadata || {};
    const details = [];

    if (metadata.crypto_type) {
        details.push(`Asset: ${metadata.crypto_type}`);
    }
    if (metadata.network) {
        details.push(`Network: ${metadata.network}`);
    }
    if (metadata.wallet_address) {
        details.push(`Wallet: ${metadata.wallet_address}`);
    }
    if (metadata.transaction_hash) {
        details.push(`Tx: ${metadata.transaction_hash}`);
    }

    if (!details.length) {
        return '';
    }

    return `
        <small style="display:block;margin-top:0.35rem;color:var(--text-muted);word-break:break-all;">
            ${escapeHtml(details.join(' | '))}
        </small>
    `;
}

function escapeHtml(value) {
    return String(value || '')
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

function escapeAttribute(value) {
    return String(value || '').replace(/'/g, "\\'");
}
