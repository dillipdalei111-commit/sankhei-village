document.addEventListener('DOMContentLoaded', () => {
    // 1. Page Loader Logic (Instant hide, no artificial link delays)
    const loader = document.getElementById('page-loader');
    if (loader) {
        // Hide loader instantly
        loader.classList.add('hidden');
    }
    window.addEventListener('pageshow', () => {
        if (loader) loader.classList.add('hidden');
    });

    // 2. Theme Toggle Logic
    const themeBtn = document.getElementById('theme-toggle');
    const currentTheme = localStorage.getItem('sankhei_theme');
    
    // Apply saved theme on load
    if (currentTheme === 'light') {
        document.body.classList.add('light-theme');
        if(themeBtn) themeBtn.textContent = '☀️';
    }

    if (themeBtn) {
        themeBtn.addEventListener('click', () => {
            document.body.classList.toggle('light-theme');
            let isLight = document.body.classList.contains('light-theme');
            
            if (isLight) {
                localStorage.setItem('sankhei_theme', 'light');
                themeBtn.textContent = '☀️';
            } else {
                localStorage.setItem('sankhei_theme', 'dark');
                themeBtn.textContent = '🌙';
            }
        });
    }

    // 3. Weather Widget Logic (With 1.5s Fast Timeout)
    const weatherTempEls = document.querySelectorAll('.weather-temp, #weather-temp');
    const weatherIconEls = document.querySelectorAll('.weather-icon, #weather-icon');
    
    if (weatherTempEls.length > 0 && weatherIconEls.length > 0) {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 1500); // 1.5s fast timeout

        fetch('https://api.open-meteo.com/v1/forecast?latitude=20.1287&longitude=85.1051&current_weather=true', { signal: controller.signal })
            .then(response => response.json())
            .then(data => {
                clearTimeout(timeoutId);
                const temp = Math.round(data.current_weather.temperature);
                const code = data.current_weather.weathercode;
                let icon = '☁️';
                
                // Set icon based on WMO weather code
                if (code === 0) icon = '☀️';
                else if (code >= 1 && code <= 3) icon = '⛅';
                else if (code >= 45 && code <= 48) icon = '🌫️';
                else if (code >= 51 && code <= 67) icon = '🌧️';
                else if (code >= 71 && code <= 77) icon = '❄️';
                else if (code >= 80 && code <= 82) icon = '🌦️';
                else if (code >= 95 && code <= 99) icon = '⛈️';

                weatherTempEls.forEach(el => { el.textContent = `${temp}°C`; });
                weatherIconEls.forEach(el => { el.textContent = icon; });
            })
            .catch(err => {
                weatherTempEls.forEach(el => { el.textContent = '28°C'; });
                weatherIconEls.forEach(el => { el.textContent = '☀️'; });
            });
    }

    // Navbar Scroll Effect
    const navbar = document.querySelector('.navbar');
    
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });

    // Mobile Menu & Off-canvas Drawer Logic
    const menuIcon = document.getElementById('menu-icon');
    const navLinks = document.getElementById('nav-links');
    const navBackdrop = document.getElementById('nav-backdrop');
    const drawerCloseBtn = document.getElementById('drawer-close-btn');

    function openMobileMenu() {
        if (navLinks) navLinks.classList.add('active');
        if (menuIcon) {
            menuIcon.classList.add('toggle');
            menuIcon.setAttribute('aria-expanded', 'true');
        }
        if (navBackdrop) navBackdrop.classList.add('active');
        document.body.classList.add('menu-open');
    }

    function closeMobileMenu() {
        if (navLinks) navLinks.classList.remove('active');
        if (menuIcon) {
            menuIcon.classList.remove('toggle');
            menuIcon.setAttribute('aria-expanded', 'false');
        }
        if (navBackdrop) navBackdrop.classList.remove('active');
        document.body.classList.remove('menu-open');
    }

    function toggleMobileMenu() {
        if (navLinks && navLinks.classList.contains('active')) {
            closeMobileMenu();
        } else {
            openMobileMenu();
        }
    }

    if (menuIcon) {
        menuIcon.addEventListener('click', (e) => {
            e.stopPropagation();
            toggleMobileMenu();
        });
    }

    if (drawerCloseBtn) {
        drawerCloseBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            closeMobileMenu();
        });
    }

    if (navBackdrop) {
        navBackdrop.addEventListener('click', closeMobileMenu);
    }

    // Close mobile menu when an anchor link is clicked
    document.querySelectorAll('.nav-links a').forEach(item => {
        item.addEventListener('click', () => {
            if (window.innerWidth <= 1024) {
                closeMobileMenu();
            }
        });
    });

    // Close mobile menu on Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && navLinks && navLinks.classList.contains('active')) {
            closeMobileMenu();
        }
    });

    // Auto close drawer when resizing to desktop
    window.addEventListener('resize', () => {
        if (window.innerWidth > 1024 && navLinks && navLinks.classList.contains('active')) {
            closeMobileMenu();
        }
    });

    // Scroll Reveal Animation (Intersection Observer)
    const revealElements = document.querySelectorAll('.scroll-reveal');

    const revealOptions = {
        threshold: 0.15,
        rootMargin: "0px 0px -50px 0px"
    };

    const revealOnScroll = new IntersectionObserver(function(entries, observer) {
        entries.forEach(entry => {
            if (!entry.isIntersecting) {
                return;
            } else {
                entry.target.classList.add('active');
                observer.unobserve(entry.target);
            }
        });
    }, revealOptions);

    revealElements.forEach(el => {
        revealOnScroll.observe(el);
    });

    // Smooth Scrolling for anchor links (fallback/enhancement)
    document.querySelectorAll('a[href^="#"], a[href^="/#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            // If it's a /# link, only smooth scroll if we are already on the homepage
            if (href.startsWith('/#') && window.location.pathname !== '/') {
                return; // Let it navigate normally to the homepage
            }
            
            const targetId = href.startsWith('/#') ? href.substring(1) : href;
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                e.preventDefault();
                targetElement.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });

    // Multi-Slideshow Logic
    const slidersData = {};

    document.querySelectorAll('.slider').forEach(slider => {
        const id = slider.id;
        if (!id) return;
        
        const slides = slider.querySelectorAll('.slide');
        if (slides.length === 0) return;

        slidersData[id] = {
            index: 0,
            slides: slides,
            dots: slider.querySelectorAll('.dot'),
            interval: null,
            sliderElement: slider
        };

        // Initialize
        showSlide(id, 0);
        startInterval(id);

        // Pause on hover
        slider.addEventListener('mouseenter', () => clearInterval(slidersData[id].interval));
        slider.addEventListener('mouseleave', () => startInterval(id));
    });

    function showSlide(id, index) {
        const data = slidersData[id];
        if (!data) return;

        if (index >= data.slides.length) data.index = 0;
        if (index < 0) data.index = data.slides.length - 1;

        data.slides.forEach(slide => slide.classList.remove('active'));
        data.dots.forEach(dot => dot.classList.remove('active'));

        if(data.slides[data.index]) data.slides[data.index].classList.add('active');
        if(data.dots[data.index]) data.dots[data.index].classList.add('active');
    }

    window.moveSlide = function(id, n) {
        if (!slidersData[id]) return;
        slidersData[id].index += n;
        showSlide(id, slidersData[id].index);
        resetInterval(id);
    };

    window.currentSlide = function(id, n) {
        if (!slidersData[id]) return;
        slidersData[id].index = n;
        showSlide(id, slidersData[id].index);
        resetInterval(id);
    };

    function startInterval(id) {
        if (!slidersData[id]) return;
        slidersData[id].interval = setInterval(() => {
            slidersData[id].index++;
            showSlide(id, slidersData[id].index);
        }, 3000);
    }

    function resetInterval(id) {
        if (!slidersData[id]) return;
        clearInterval(slidersData[id].interval);
        startInterval(id);
    }
    // 4. Live IST Clock Logic
    const clockTimeEls = document.querySelectorAll('.clock-time, #clock-time');
    function updateClock() {
        if (clockTimeEls.length === 0) return;
        const now = new Date();
        // Format as Indian Standard Time (IST)
        const options = { timeZone: 'Asia/Kolkata', hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: true };
        const timeStr = now.toLocaleTimeString('en-IN', options);
        clockTimeEls.forEach(el => { el.textContent = timeStr; });
    }
    if (clockTimeEls.length > 0) {
        updateClock();
        setInterval(updateClock, 1000);
    }

    // 5. Language Switcher Logic (English / Odia - ଓଡ଼ିଆ)
    const langToggleBtns = document.querySelectorAll('.lang-toggle-btn, #lang-toggle');
    const langLabels = document.querySelectorAll('.lang-label, #lang-label');
    let currentLang = localStorage.getItem('sankhei_lang') || 'en';

    function setLanguage(lang) {
        currentLang = lang;
        localStorage.setItem('sankhei_lang', lang);
        langLabels.forEach(el => {
            el.textContent = lang === 'or' ? 'ଓଡ଼ିଆ' : 'EN';
        });
        
        document.querySelectorAll('[data-en][data-or]').forEach(el => {
            const text = el.getAttribute(`data-${lang}`);
            if (text) {
                if (el.tagName === 'INPUT' && el.type === 'text') {
                    el.placeholder = text;
                } else {
                    el.textContent = text;
                }
            }
        });
    }

    setLanguage(currentLang);
    langToggleBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const nextLang = currentLang === 'en' ? 'or' : 'en';
            setLanguage(nextLang);
        });
    });

    // 6. Lightbox Modal Logic
    const lightboxModal = document.getElementById('lightbox-modal');
    const lightboxImg = document.getElementById('lightbox-img');
    const lightboxCaption = document.getElementById('lightbox-caption');
    const lightboxClose = document.getElementById('lightbox-close');

    if (lightboxModal && lightboxImg) {
        document.querySelectorAll('.lightbox-trigger').forEach(item => {
            item.addEventListener('click', (e) => {
                const img = item.querySelector('img') || item;
                const captionText = item.getAttribute('data-caption') || img.alt || '';
                
                lightboxImg.src = img.src;
                if (lightboxCaption) lightboxCaption.textContent = captionText;
                lightboxModal.classList.add('active');
            });
        });

        if (lightboxClose) {
            lightboxClose.addEventListener('click', () => {
                lightboxModal.classList.remove('active');
            });
        }

        lightboxModal.addEventListener('click', (e) => {
            if (e.target === lightboxModal) {
                lightboxModal.classList.remove('active');
            }
        });
    }

    // 7. Floating Back to Top Button Logic
    const backToTopBtn = document.getElementById('back-to-top');
    if (backToTopBtn) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 350) {
                backToTopBtn.classList.add('show');
            } else {
                backToTopBtn.classList.remove('show');
            }
        });

        backToTopBtn.addEventListener('click', () => {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }

    // 8. Festival Countdown Clock (Danda Yatra - April 14, 2027)
    const cdDays = document.getElementById('cd-days');
    const cdHours = document.getElementById('cd-hours');
    const cdMins = document.getElementById('cd-mins');
    const cdSecs = document.getElementById('cd-secs');

    function updateFestivalCountdown() {
        if (!cdDays) return;
        const festivalDate = new Date('April 14, 2027 00:00:00').getTime();
        const now = new Date().getTime();
        const diff = festivalDate - now;

        if (diff <= 0) {
            if (cdDays) cdDays.textContent = '00';
            return;
        }

        const days = Math.floor(diff / (1000 * 60 * 60 * 24));
        const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const mins = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
        const secs = Math.floor((diff % (1000 * 60)) / 1000);

        cdDays.textContent = String(days).padStart(2, '0');
        cdHours.textContent = String(hours).padStart(2, '0');
        cdMins.textContent = String(mins).padStart(2, '0');
        cdSecs.textContent = String(secs).padStart(2, '0');
    }

    if (cdDays) {
        updateFestivalCountdown();
        setInterval(updateFestivalCountdown, 1000);
    }

    // 9. Web Audio API Peaceful Ambient Flute / Chime Player
    const audioBtn = document.getElementById('ambient-audio-btn');
    const audioLabel = document.getElementById('audio-label');
    let audioCtx = null;
    let isPlayingAudio = false;
    let timerId = null;

    function playAmbientNote() {
        if (!isPlayingAudio || !audioCtx) return;
        
        // Pentatonic scale frequencies in Hz (A3, C4, D4, E4, G4, A4)
        const notes = [220.00, 261.63, 293.66, 329.63, 392.00, 440.00];
        const freq = notes[Math.floor(Math.random() * notes.length)];

        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();

        osc.type = 'sine'; // Smooth flute-like sine wave
        osc.frequency.setValueAtTime(freq, audioCtx.currentTime);

        // Soft envelope: attack 0.5s, decay 2.5s
        gain.gain.setValueAtTime(0, audioCtx.currentTime);
        gain.gain.linearRampToValueAtTime(0.06, audioCtx.currentTime + 0.5);
        gain.gain.exponentialRampToValueAtTime(0.0001, audioCtx.currentTime + 3.0);

        osc.connect(gain);
        gain.connect(audioCtx.destination);

        osc.start();
        osc.stop(audioCtx.currentTime + 3.1);
    }

    if (audioBtn) {
        audioBtn.addEventListener('click', () => {
            if (!isPlayingAudio) {
                if (!audioCtx) {
                    const AudioContext = window.AudioContext || window.webkitAudioContext;
                    audioCtx = new AudioContext();
                }
                if (audioCtx.state === 'suspended') {
                    audioCtx.resume();
                }
                isPlayingAudio = true;
                if (audioLabel) audioLabel.textContent = '🎵 Sound ON';
                audioBtn.style.borderColor = 'var(--accent)';
                playAmbientNote();
                timerId = setInterval(playAmbientNote, 2200);
            } else {
                isPlayingAudio = false;
                if (timerId) clearInterval(timerId);
                if (audioLabel) audioLabel.textContent = '🔇 Sound OFF';
                audioBtn.style.borderColor = 'rgba(255,255,255,0.25)';
            }
        });
    }

    // 10. Printable Directory Button Trigger
    document.querySelectorAll('.print-directory-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            window.print();
        });
    });
});


