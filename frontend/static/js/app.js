// API Base URL
const API_BASE_URL = '/api';

// Load site settings on page load
document.addEventListener('DOMContentLoaded', function() {
    loadSiteSettings();
    setupWithdrawalPopups();
    setupPopupNotifications();
});

// Load site settings from backend
async function loadSiteSettings() {
    try {
        const response = await fetch(`${API_BASE_URL}/admin/settings/get_settings/`);
        if (response.ok) {
            const data = await response.json();
            updateFooterSettings(data);
        }
    } catch (error) {
        console.log('Settings load error:', error);
    }
}

// Update footer with dynamic settings
function updateFooterSettings(settings) {
    const footerContact = document.getElementById('footer-contact');
    const footerText = document.getElementById('footer-text');
    
    if (footerContact) {
        footerContact.innerHTML = `
            📧 ${settings.support_email}<br>
            📞 ${settings.support_phone}<br>
            📍 ${settings.support_address}
        `;
    }
    
    if (footerText) {
        footerText.textContent = settings.footer_text || '© 2024 Broker Invest. All rights reserved.';
    }
}

// Setup withdrawal popups to show random recent withdrawals
function setupWithdrawalPopups() {
    setInterval(async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/admin/popup-notifications/recent_notifications/`);
            if (response.ok) {
                const notifications = await response.json();
                if (notifications.length > 0) {
                    const randomNotification = notifications[Math.floor(Math.random() * notifications.length)];
                    showWithdrawalPopup(randomNotification);
                }
            }
        } catch (error) {
            console.log('Popup notifications error:', error);
        }
    }, 15000); // Show popup every 15 seconds
}

// Show random withdrawal popup
function showWithdrawalPopup(notification) {
    const popup = document.getElementById('withdrawalPopup');
    const popupText = document.getElementById('popupText');
    
    if (popup && popupText) {
        popupText.innerHTML = `
            <strong>💸 ${notification.username}</strong> just withdrew 
            <strong>$${parseFloat(notification.amount).toFixed(2)}</strong>
        `;
        popup.classList.remove('hidden');
        
        setTimeout(() => {
            popup.classList.add('hidden');
        }, 5000);
    }
}

// Close withdrawal popup
function closeWithdrawalPopup() {
    const popup = document.getElementById('withdrawalPopup');
    if (popup) {
        popup.classList.add('hidden');
    }
}

// Setup popup notifications for dashboard
function setupPopupNotifications() {
    if (document.body.classList.contains('dashboard-page')) {
        setInterval(async () => {
            const user = JSON.parse(localStorage.getItem('user') || '{}');
            if (user.id) {
                try {
                    const response = await fetch(`${API_BASE_URL}/admin/popup-notifications/recent_notifications/`);
                    if (response.ok) {
                        const notifications = await response.json();
                        if (notifications.length > 0) {
                            const randomNotification = notifications[Math.floor(Math.random() * notifications.length)];
                            showWithdrawalPopup(randomNotification);
                        }
                    }
                } catch (error) {
                    console.log('Error loading notifications:', error);
                }
            }
        }, 20000); // Show every 20 seconds on dashboard
    }
}

// Copy to clipboard function
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        alert('Copied to clipboard!');
    }).catch(() => {
        alert('Failed to copy');
    });
}

// Check authentication
function checkAuth() {
    const user = localStorage.getItem('user');
    if (!user && window.location.pathname.includes('dashboard')) {
        window.location.href = '/login';
    }
}

// Logout function
function logout() {
    localStorage.removeItem('user');
    localStorage.removeItem('profile');
    localStorage.removeItem('token');
    window.location.href = '/';
}

// Setup navigation clicks
document.addEventListener('DOMContentLoaded', function() {
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Remove active from all items
            navItems.forEach(i => i.classList.remove('active'));
            // Add active to clicked item
            this.classList.add('active');
            
            // Hide all sections
            const sections = document.querySelectorAll('.dashboard-section');
            sections.forEach(s => s.classList.remove('active'));
            
            // Show selected section
            const sectionName = this.getAttribute('data-section');
            const section = document.getElementById(sectionName + '-section');
            if (section) {
                section.classList.add('active');
            }
        });
    });

    // Logout button
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', logout);
    }

    checkAuth();
});
