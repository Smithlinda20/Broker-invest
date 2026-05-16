const adminState = {
    section: 'activities',
};

document.addEventListener('DOMContentLoaded', async () => {
    try {
        await refreshSummary();
        await loadSection('activities');
    } catch (error) {
        console.error('Admin dashboard init failed:', error);
    }
});

async function adminFetchJson(url, options = {}) {
    const response = await fetch(url, {
        credentials: 'same-origin',
        ...options,
        headers: {
            'Content-Type': 'application/json',
            ...(options.headers || {}),
        },
    });

    const data = await response.json();
    if (!response.ok) {
        throw new Error(data.error || data.message || 'Request failed');
    }

    return data;
}

async function refreshSummary() {
    const summary = await adminFetchJson('/backend/api/summary/', { headers: { 'Content-Type': 'application/json' } });
    setAdminText('statUsers', summary.total_users || 0);
    setAdminText('statPending', summary.pending_payments || 0);
    setAdminText('statWithdrawals', summary.pending_withdrawals || 0);
    setAdminText('statInvestments', summary.active_investments || 0);
    setAdminText('statTotalWithdrawn', formatAdminCurrency(summary.total_withdrawn || 0));
}

async function loadSection(section) {
    adminState.section = section;
    setActiveNav(section);

    const titleElement = document.querySelector('.section-title');
    if (titleElement) {
        titleElement.textContent = sectionTitle(section);
    }

    const filters = document.querySelector('.filter-controls');
    const headerRow = document.getElementById('tableHeaderRow');
    const filterType = document.getElementById('filterType');
    const filterStatus = document.getElementById('filterStatus');

    if (section === 'users') {
        if (filters) filters.style.display = 'none';
        if (headerRow) {
            headerRow.innerHTML = `
                <th>User</th>
                <th>Email</th>
                <th>Balance</th>
                <th>Referral Code</th>
                <th>Active Investments</th>
                <th>Pending Payments</th>
                <th>Pending Withdrawals</th>
                <th>Date Joined</th>
            `;
        }
        await loadUsers();
        return;
    }

    if (filters) filters.style.display = 'flex';
    if (headerRow) {
        headerRow.innerHTML = `
            <th>User</th>
            <th>Activity</th>
            <th>Description</th>
            <th>Amount</th>
            <th>Plan</th>
            <th>Status</th>
            <th>Date</th>
            <th>Action</th>
        `;
    }

    if (filterType) {
        filterType.value = section === 'payments'
            ? 'payment_pending'
            : section === 'withdrawals'
                ? 'withdrawal_requested'
                : section === 'investments'
                    ? 'investment'
                    : '';
    }

    if (filterStatus && section !== 'activities') {
        filterStatus.value = '';
    }

    await loadActivities();
}

async function loadActivities() {
    if (adminState.section === 'users') {
        await loadUsers();
        return;
    }

    const filterType = document.getElementById('filterType')?.value || '';
    const filterStatus = document.getElementById('filterStatus')?.value || '';
    const params = new URLSearchParams();

    if (filterType) params.set('type', filterType);
    if (filterStatus) params.set('status', filterStatus);
    if (adminState.section && adminState.section !== 'activities') params.set('section', adminState.section);

    try {
        const url = `/backend/api/activities/${params.toString() ? `?${params.toString()}` : ''}`;
        const activities = await adminFetchJson(url, { headers: { 'Content-Type': 'application/json' } });
        renderActivities(activities);
    } catch (error) {
        console.error('Error loading activities:', error);
        renderEmptyRow('Error loading activities', 8);
    }
}

function renderActivities(activities) {
    const tbody = document.getElementById('activityTableBody');
    if (!tbody) return;

    if (!activities.length) {
        renderEmptyRow('No activities found', 8);
        return;
    }

    tbody.innerHTML = activities.map((activity) => `
        <tr>
            <td>${escapeAdminHtml(activity.username)}<br><small>${escapeAdminHtml(activity.email || '-')}</small></td>
            <td>${formatActivityType(activity.activity_type)}</td>
            <td>${renderAdminActivityDescription(activity)}</td>
            <td>${activity.amount ? formatAdminCurrency(activity.amount) : '-'}</td>
            <td>${escapeAdminHtml(activity.plan || '-')}</td>
            <td><span class="status-badge status-${activity.status}">${capitalizeAdmin(activity.status)}</span></td>
            <td>${new Date(activity.created_at).toLocaleString()}</td>
            <td>${renderActivityActions(activity)}</td>
        </tr>
    `).join('');
}

async function loadUsers() {
    try {
        const users = await adminFetchJson('/backend/api/users/', { headers: { 'Content-Type': 'application/json' } });
        renderUsers(users);
    } catch (error) {
        console.error('Error loading users:', error);
        renderEmptyRow('Error loading users', 8);
    }
}

function renderUsers(users) {
    const tbody = document.getElementById('activityTableBody');
    if (!tbody) return;

    if (!users.length) {
        renderEmptyRow('No users found', 8);
        return;
    }

    tbody.innerHTML = users.map((user) => `
        <tr>
            <td>${escapeAdminHtml(user.username)}</td>
            <td>${escapeAdminHtml(user.email || '-')}</td>
            <td>${formatAdminCurrency(user.balance)}</td>
            <td>${escapeAdminHtml(user.referral_code)}</td>
            <td>${user.active_investments}</td>
            <td>${user.pending_payments}</td>
            <td>${user.pending_withdrawals}</td>
            <td>${new Date(user.joined_at).toLocaleDateString()}</td>
        </tr>
    `).join('');
}

function renderActivityActions(activity) {
    if (!activity.available_actions || !activity.available_actions.length) {
        return '—';
    }

    return `
        <div class="action-buttons">
            <button class="btn-sm btn-confirm" onclick="confirmPayment('${activity.id}')">Confirm</button>
            <button class="btn-sm btn-reject" onclick="rejectPayment('${activity.id}')">Reject</button>
        </div>
    `;
}

function renderAdminActivityDescription(activity) {
    const metadata = activity?.metadata || {};
    const lines = [escapeAdminHtml(activity.description || '-')];

    if (metadata.crypto_type) {
        lines.push(`Asset: ${escapeAdminHtml(metadata.crypto_type)}`);
    }
    if (metadata.network) {
        lines.push(`Network: ${escapeAdminHtml(metadata.network)}`);
    }
    if (metadata.wallet_address) {
        lines.push(`Wallet: ${escapeAdminHtml(metadata.wallet_address)}`);
    }
    if (metadata.transaction_hash) {
        lines.push(`Tx Hash: ${escapeAdminHtml(metadata.transaction_hash)}`);
    }
    if (activity.reviewed_by) {
        lines.push(`Reviewed By: ${escapeAdminHtml(activity.reviewed_by)}`);
    }
    if (activity.admin_note) {
        lines.push(`Note: ${escapeAdminHtml(activity.admin_note)}`);
    }

    return lines.map((line, index) => {
        if (index === 0) {
            return `<div>${line}</div>`;
        }
        return `<small style="display:block;color:#94a3b8;word-break:break-all;margin-top:0.25rem;">${line}</small>`;
    }).join('');
}

function renderEmptyRow(message, colspan) {
    const tbody = document.getElementById('activityTableBody');
    if (!tbody) return;

    tbody.innerHTML = `
        <tr>
            <td colspan="${colspan}" class="empty-state">
                <p>${message}</p>
            </td>
        </tr>
    `;
}

async function confirmPayment(activityId) {
    if (!confirm('Confirm this activity?')) return;

    try {
        const result = await adminFetchJson('/backend/api/confirm-payment/', {
            method: 'POST',
            body: JSON.stringify({ activity_id: activityId }),
        });
        alert(result.message || 'Confirmed successfully');
        await refreshSummary();
        await loadSection(adminState.section);
    } catch (error) {
        alert(error.message);
    }
}

async function rejectPayment(activityId) {
    if (!confirm('Reject this activity?')) return;

    try {
        const result = await adminFetchJson('/backend/api/reject-payment/', {
            method: 'POST',
            body: JSON.stringify({ activity_id: activityId }),
        });
        alert(result.message || 'Rejected successfully');
        await refreshSummary();
        await loadSection(adminState.section);
    } catch (error) {
        alert(error.message);
    }
}

async function logoutAdmin() {
    try {
        await fetch('/backend/logout/', { method: 'POST', credentials: 'same-origin' });
    } finally {
        window.location.href = '/backend/login/';
    }
}

function setActiveNav(section) {
    document.querySelectorAll('.admin-nav-link').forEach((link) => link.classList.remove('active'));
    const link = Array.from(document.querySelectorAll('.admin-nav-link'))
        .find((item) => item.getAttribute('onclick')?.includes(`'${section}'`));
    link?.classList.add('active');
}

function sectionTitle(section) {
    return {
        activities: 'All Activities',
        payments: 'Payment Verification',
        withdrawals: 'Withdrawals',
        investments: 'Investments',
        users: 'Registered Users',
    }[section] || 'Admin Dashboard';
}

function setAdminText(id, value) {
    const element = document.getElementById(id);
    if (element) element.textContent = value;
}

function formatActivityType(value) {
    return String(value || '').replace(/_/g, ' ').replace(/\b\w/g, (char) => char.toUpperCase());
}

function capitalizeAdmin(value) {
    return String(value || '').replace(/\b\w/g, (char) => char.toUpperCase());
}

function formatAdminCurrency(value) {
    const numeric = Number.parseFloat(value || 0);
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(
        Number.isFinite(numeric) ? numeric : 0
    );
}

function escapeAdminHtml(value) {
    return String(value || '')
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}
