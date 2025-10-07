/**
 * Chain-of-Thought Hijacking Website
 * Interactive JavaScript Functions
 */

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    initNavbar();
    initMobileMenu();
    initBackToTop();
    initSmoothScroll();
    initCopyBibtex();
    initResultsChart();
    initImageZoom();
});

/**
 * Navbar scroll effect
 */
function initNavbar() {
    const navbar = document.getElementById('navbar');

    window.addEventListener('scroll', function() {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });

    // Highlight active nav link based on scroll position
    const sections = document.querySelectorAll('section[id]');
    const navLinks = document.querySelectorAll('.nav-link');

    window.addEventListener('scroll', () => {
        let current = '';

        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.clientHeight;

            if (window.pageYOffset >= sectionTop - 100) {
                current = section.getAttribute('id');
            }
        });

        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === `#${current}`) {
                link.classList.add('active');
            }
        });
    });
}

/**
 * Mobile menu toggle
 */
function initMobileMenu() {
    const navToggle = document.getElementById('nav-toggle');
    const navMenu = document.getElementById('nav-menu');

    if (navToggle && navMenu) {
        navToggle.addEventListener('click', function() {
            navMenu.classList.toggle('active');

            // Animate hamburger icon
            const spans = this.querySelectorAll('span');
            if (navMenu.classList.contains('active')) {
                spans[0].style.transform = 'rotate(45deg) translate(5px, 5px)';
                spans[1].style.opacity = '0';
                spans[2].style.transform = 'rotate(-45deg) translate(7px, -6px)';
            } else {
                spans[0].style.transform = 'none';
                spans[1].style.opacity = '1';
                spans[2].style.transform = 'none';
            }
        });

        // Close menu when clicking a link
        const navLinks = navMenu.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                navMenu.classList.remove('active');
                const spans = navToggle.querySelectorAll('span');
                spans[0].style.transform = 'none';
                spans[1].style.opacity = '1';
                spans[2].style.transform = 'none';
            });
        });
    }
}

/**
 * Back to top button
 */
function initBackToTop() {
    const backToTopBtn = document.getElementById('back-to-top');

    if (backToTopBtn) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 300) {
                backToTopBtn.classList.add('visible');
            } else {
                backToTopBtn.classList.remove('visible');
            }
        });

        backToTopBtn.addEventListener('click', function() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }
}

/**
 * Smooth scrolling for anchor links
 */
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');

            // Skip if it's just '#'
            if (href === '#') return;

            e.preventDefault();

            const target = document.querySelector(href);
            if (target) {
                const navbarHeight = document.getElementById('navbar').offsetHeight;
                const targetPosition = target.offsetTop - navbarHeight - 20;

                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });
}

/**
 * Copy BibTeX to clipboard
 */
function initCopyBibtex() {
    const copyBtn = document.getElementById('copy-bibtex');
    const bibtexContent = document.getElementById('bibtex-content');

    if (copyBtn && bibtexContent) {
        copyBtn.addEventListener('click', function() {
            const text = bibtexContent.textContent;

            // Modern clipboard API
            if (navigator.clipboard) {
                navigator.clipboard.writeText(text).then(() => {
                    showCopyFeedback(copyBtn, '✓ Copied!');
                }).catch(err => {
                    console.error('Failed to copy:', err);
                    fallbackCopy(text, copyBtn);
                });
            } else {
                fallbackCopy(text, copyBtn);
            }
        });
    }
}

/**
 * Fallback copy method for older browsers
 */
function fallbackCopy(text, btn) {
    const textarea = document.createElement('textarea');
    textarea.value = text;
    textarea.style.position = 'fixed';
    textarea.style.opacity = '0';
    document.body.appendChild(textarea);
    textarea.select();

    try {
        document.execCommand('copy');
        showCopyFeedback(btn, '✓ Copied!');
    } catch (err) {
        showCopyFeedback(btn, '✗ Failed');
    }

    document.body.removeChild(textarea);
}

/**
 * Show copy feedback
 */
function showCopyFeedback(btn, message) {
    const originalText = btn.textContent;
    btn.textContent = message;
    btn.style.background = '#10b981';

    setTimeout(() => {
        btn.textContent = originalText;
        btn.style.background = '';
    }, 2000);
}

/**
 * Initialize results comparison chart
 */
function initResultsChart() {
    const canvas = document.getElementById('resultsChart');

    if (!canvas || typeof Chart === 'undefined') return;

    const ctx = canvas.getContext('2d');

    const data = {
        labels: ['Gemini 2.5 Pro', 'GPT-o4 Mini', 'Grok 3 Mini', 'Claude 4 Sonnet'],
        datasets: [
            {
                label: 'Mousetrap',
                data: [44, 25, 60, 22],
                backgroundColor: 'rgba(100, 116, 139, 0.7)',
                borderColor: 'rgba(100, 116, 139, 1)',
                borderWidth: 2
            },
            {
                label: 'H-CoT',
                data: [60, 65, 66, 11],
                backgroundColor: 'rgba(251, 146, 60, 0.7)',
                borderColor: 'rgba(251, 146, 60, 1)',
                borderWidth: 2
            },
            {
                label: 'AutoRAN',
                data: [69, 47, 61, 5],
                backgroundColor: 'rgba(59, 130, 246, 0.7)',
                borderColor: 'rgba(59, 130, 246, 1)',
                borderWidth: 2
            },
            {
                label: 'CoT Hijacking (Ours)',
                data: [99, 94, 100, 94],
                backgroundColor: 'rgba(102, 126, 234, 0.8)',
                borderColor: 'rgba(118, 75, 162, 1)',
                borderWidth: 3
            }
        ]
    };

    const config = {
        type: 'bar',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        font: {
                            size: 13,
                            family: "'Inter', sans-serif"
                        },
                        padding: 15,
                        usePointStyle: true
                    }
                },
                title: {
                    display: true,
                    text: 'Attack Success Rate (%) Comparison',
                    font: {
                        size: 18,
                        weight: 'bold',
                        family: "'Inter', sans-serif"
                    },
                    padding: 20
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    padding: 12,
                    titleFont: {
                        size: 14
                    },
                    bodyFont: {
                        size: 13
                    },
                    callbacks: {
                        label: function(context) {
                            return context.dataset.label + ': ' + context.parsed.y + '%';
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 105,
                    ticks: {
                        callback: function(value) {
                            return value + '%';
                        },
                        font: {
                            size: 12
                        }
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                },
                x: {
                    ticks: {
                        font: {
                            size: 12
                        }
                    },
                    grid: {
                        display: false
                    }
                }
            },
            interaction: {
                mode: 'index',
                intersect: false
            }
        }
    };

    new Chart(ctx, config);
}

/**
 * Image zoom on click
 */
function initImageZoom() {
    const images = document.querySelectorAll('.analysis-img, .figure-img');

    images.forEach(img => {
        img.style.cursor = 'pointer';

        img.addEventListener('click', function() {
            createImageModal(this.src, this.alt);
        });
    });
}

/**
 * Create modal for image zoom
 */
function createImageModal(src, alt) {
    // Create modal overlay
    const modal = document.createElement('div');
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.9);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10000;
        cursor: zoom-out;
        padding: 20px;
    `;

    // Create image
    const img = document.createElement('img');
    img.src = src;
    img.alt = alt;
    img.style.cssText = `
        max-width: 95%;
        max-height: 95%;
        object-fit: contain;
        border-radius: 8px;
        box-shadow: 0 10px 50px rgba(0, 0, 0, 0.5);
    `;

    // Create close button
    const closeBtn = document.createElement('button');
    closeBtn.textContent = '×';
    closeBtn.style.cssText = `
        position: absolute;
        top: 20px;
        right: 30px;
        background: white;
        border: none;
        font-size: 40px;
        width: 50px;
        height: 50px;
        border-radius: 50%;
        cursor: pointer;
        line-height: 50px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        transition: all 0.3s;
    `;

    closeBtn.onmouseover = () => {
        closeBtn.style.background = '#ef4444';
        closeBtn.style.color = 'white';
        closeBtn.style.transform = 'rotate(90deg)';
    };

    closeBtn.onmouseout = () => {
        closeBtn.style.background = 'white';
        closeBtn.style.color = 'black';
        closeBtn.style.transform = 'rotate(0deg)';
    };

    // Append elements
    modal.appendChild(img);
    modal.appendChild(closeBtn);
    document.body.appendChild(modal);

    // Prevent body scroll
    document.body.style.overflow = 'hidden';

    // Close modal on click
    const closeModal = () => {
        document.body.removeChild(modal);
        document.body.style.overflow = '';
    };

    modal.addEventListener('click', function(e) {
        if (e.target === modal || e.target === closeBtn) {
            closeModal();
        }
    });

    // Close on ESC key
    document.addEventListener('keydown', function escHandler(e) {
        if (e.key === 'Escape') {
            closeModal();
            document.removeEventListener('keydown', escHandler);
        }
    });
}

/**
 * Animate elements on scroll (simple AOS alternative)
 */
function animateOnScroll() {
    const elements = document.querySelectorAll('[data-aos]');

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, {
        threshold: 0.1
    });

    elements.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });
}

// Initialize animation on scroll if IntersectionObserver is supported
if ('IntersectionObserver' in window) {
    animateOnScroll();
}

/**
 * Console easter egg
 */
console.log(
    '%c⚠️ Chain-of-Thought Hijacking Research ⚠️',
    'font-size: 20px; font-weight: bold; color: #667eea;'
);
console.log(
    '%cThis research is for defensive security purposes only.',
    'font-size: 14px; color: #64748b;'
);
console.log(
    '%c🔗 GitHub: https://github.com/girlsuuu/Hijacking',
    'font-size: 12px; color: #10b981;'
);
