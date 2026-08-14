/* ==========================================================================
   CYBER FRAUD TRANSACTION ANALYSIS & DETECTION SYSTEM
   Frontend JavaScript Engine (SOC Dashboard Interactive Client)
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Live Header Clock & Last Updated Timer
    function updateClock() {
        const now = new Date();
        const options = { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: true };
        const clockStr = now.toLocaleDateString('en-GB', options).replace(',', ' |');
        
        const clockEl = document.getElementById('liveClock');
        if (clockEl) clockEl.innerText = clockStr;

        const updatedEl = document.getElementById('lastUpdatedTime');
        if (updatedEl) updatedEl.innerText = `Last Updated: ${now.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}`;
    }
    updateClock();
    setInterval(updateClock, 1000);

    // 2. Sidebar & Mobile Active Nav Highlighting
    const navItems = document.querySelectorAll('.nav-item, .mobile-nav-item');
    navItems.forEach(item => {
        item.addEventListener('click', () => {
            navItems.forEach(nav => nav.classList.remove('active'));
            item.classList.add('active');
        });
    });

    // 3. Interactive Transaction Risk Analyzer Form Submission
    const predictForm = document.getElementById('analyzeForm');
    if (predictForm) {
        predictForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const submitBtn = document.getElementById('submitBtn');
            const originalText = submitBtn.innerHTML;
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span>⚡ SCANNING TRANSACTION...</span>';

            const payload = {
                amount: parseFloat(document.getElementById('txAmount').value),
                merchant_id: parseInt(document.getElementById('txMerchant').value),
                transaction_type: document.getElementById('txType').value,
                location: document.getElementById('txLocation').value,
                hour: parseInt(document.getElementById('txHour').value) || 14
            };

            try {
                const response = await fetch('/api/predict', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });

                const data = await response.json();
                if (data.status === 'success') {
                    displayPredictionResult(data.result);
                } else {
                    alert('Prediction Error: ' + (data.message || 'Unable to analyze transaction.'));
                }
            } catch (err) {
                console.error('API Error:', err);
                alert('Server connection error. Please ensure Flask server is active.');
            } finally {
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalText;
            }
        });
    }
});

function displayPredictionResult(result) {
    const card = document.getElementById('predictionResultCard');
    const predVal = document.getElementById('resPrediction');
    const probVal = document.getElementById('resProbability');
    const progressBar = document.getElementById('resProgressBar');
    const riskBadge = document.getElementById('resRiskLevel');
    const alertMsg = document.getElementById('resAlertMsg');

    if (!card) return;

    // Reset alert box modifier class
    card.classList.remove('genuine');

    if (result.prediction === 'FRAUDULENT') {
        predVal.innerText = 'FRAUDULENT TRANSACTION';
        predVal.style.color = '#EF4444';
        probVal.style.color = '#EF4444';
        riskBadge.style.color = '#EF4444';
        riskBadge.style.borderColor = '#EF4444';
        riskBadge.style.background = 'rgba(239, 68, 68, 0.2)';
        progressBar.style.backgroundColor = '#EF4444';
        alertMsg.innerText = '⚠️ Warning: High probability of fraudulent anomaly detected. Recommend transaction decline.';
    } else {
        card.classList.add('genuine');
        predVal.innerText = 'GENUINE TRANSACTION';
        predVal.style.color = '#10B981';
        probVal.style.color = '#10B981';
        riskBadge.style.color = '#10B981';
        riskBadge.style.borderColor = '#10B981';
        riskBadge.style.background = 'rgba(16, 185, 129, 0.2)';
        progressBar.style.backgroundColor = '#10B981';
        alertMsg.innerText = '✓ Transaction verified safe. Characteristics align with normal behavior parameters.';
    }

    probVal.innerText = `${result.fraud_probability}%`;
    progressBar.style.width = `${result.fraud_probability}%`;
    riskBadge.innerText = result.risk_level;

    card.scrollIntoView({ behavior: 'smooth', block: 'center' });
}
