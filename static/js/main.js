document.addEventListener('DOMContentLoaded', function () {
    // Password visibility toggle
    document.querySelectorAll('.password-toggle span').forEach(function (toggle) {
        toggle.addEventListener('click', function () {
            const input = toggle.parentElement.querySelector('input');
            if (input.type === 'password') {
                input.type = 'text';
                toggle.textContent = 'Hide';
            } else {
                input.type = 'password';
                toggle.textContent = 'Show';
            }
        });
    });

    // Password strength meter
    const pw1 = document.querySelector('#id_password1');
    const strengthFill = document.querySelector('.strength-fill');
    if (pw1 && strengthFill) {
        pw1.addEventListener('input', function () {
            const val = pw1.value;
            let score = 0;
            if (val.length >= 8) score++;
            if (/[A-Z]/.test(val)) score++;
            if (/[0-9]/.test(val)) score++;
            if (/[^A-Za-z0-9]/.test(val)) score++;
            const pct = (score / 4) * 100;
            const colors = ['#ef4444', '#f59e0b', '#f59e0b', '#10b981'];
            strengthFill.style.width = pct + '%';
            strengthFill.style.background = colors[Math.max(score - 1, 0)];
        });
    }

    // Auto-dismiss alerts
    document.querySelectorAll('.alert').forEach(function (el) {
        setTimeout(function () {
            el.style.transition = 'opacity 0.5s';
            el.style.opacity = '0';
            setTimeout(function () { el.remove(); }, 500);
        }, 4000);
    });
});
