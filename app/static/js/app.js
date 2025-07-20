// app/static/js/app.js --- АБСОЛЮТНО ПОЛНЫЙ КОД

document.addEventListener('DOMContentLoaded', () => {
    // --- Инициализация приложения и API Telegram ---
    const tg = window.Telegram.WebApp;
    if (tg) {
        tg.ready();
        tg.expand();
        tg.setHeaderColor(tg.themeParams.secondary_bg_color || '#f3f3f3');
    }

    const appContainer = document.querySelector('.app-container');
    const pages = document.querySelectorAll('.page');
    const navItems = document.querySelectorAll('.nav-item');
    const navBar = document.querySelector('.bottom-nav');
    const contentSpacer = document.querySelector('.content-spacer');

    // === ДИНАМИЧЕСКИЙ ОТСТУП ===
    const setSpacerHeight = () => {
        if (navBar && contentSpacer) {
            contentSpacer.style.height = `${navBar.offsetHeight}px`;
        }
    };
    
    // === БАЗА ДАННЫХ ВИДЕО ===
    const videoDatabase = {
        'amir_temur': {
            title_ru: 'Монолог Амира Темура',
            title_uz: 'Amir Temur monologi',
            title_en: 'Monologue of Amir Temur',
            video_url: '/static/videos/amir_temur_monologue.mp4'
        },
    };

    // === МОДАЛЬНОЕ ОКНО ДЛЯ ВИДЕО ===
    const showVideoModal = (videoId) => {
        const videoData = videoDatabase[videoId];
        if (!videoData) { console.error(`Видео с ID "${videoId}" не найдено`); return; }
        const modalOverlay = document.createElement('div');
        modalOverlay.className = 'video-modal-overlay';
        const modalContent = document.createElement('div');
        modalContent.className = 'video-modal-content';
        const videoTitle = document.createElement('h3');
        videoTitle.textContent = videoData[`title_${currentLanguage}`] || videoData.title_ru;
        const videoPlayer = document.createElement('video');
        videoPlayer.src = videoData.video_url;
        videoPlayer.controls = true; videoPlayer.autoplay = true; videoPlayer.playsInline = true;
        modalContent.appendChild(videoTitle);
        modalContent.appendChild(videoPlayer);
        modalOverlay.appendChild(modalContent);
        modalOverlay.addEventListener('click', () => {
            videoPlayer.pause();
            modalOverlay.remove();
        });
        document.body.appendChild(modalOverlay);
    };
    
    // =======================================periodLabel========
    // --- БЛОК МУЛЬТИЯЗЫЧНОСТИ ---
    // ===============================================
    const translations = {
        ru: { exhibitions: 'Выставки', museums: 'Музеи', routes: 'Маршруты', allExhibitions: 'Все выставки', allMuseums: 'Все музеи', allRoutes: 'Все маршруты', more: 'ЕЩЁ', scanTitle: 'Интерактивный гид', scanSubheader: 'Распознайте экспонаты с помощью камеры', nearbyExhibits: 'Экспонаты рядом', catalog: 'Каталог', language: 'Язык', navRecommend: 'Рекомендуем', navInMuseum: 'Я в музее', navCatalog: 'Каталог', navProfile: 'Профиль', scanButtonText: 'Сканировать экспонат', popupTitle: 'Источник фото', popupMessage: 'Как вы хотите получить изображение?', popupCamera: 'Сделать фото', popupGallery: 'Выбрать из галереи', wipSubtitle: 'Этот раздел скоро появится', loadingError: 'Не удалось загрузить', newsError: 'Новости не найдены', themeLabel: 'Тёмная тема', themeLabelDark: 'Тёмная тема', themeLabelLight: 'Светлая тема', aiContext: "Исторический контекст", aiFact: "Интересный факт", periodLabel: 'Период:', descriptionLabel: 'Описание:', contextLabel: 'Контекст:', factLabel: 'Интересный факт:'},
        uz: { exhibitions: 'Ko\'rgazmalar', navImmersion: 'Sho\'ng\'ish', museums: 'Muzeylar', routes: 'Marshrutlar', allExhibitions: 'Barcha ko\'rgazmalar', allMuseums: 'Barcha muzeylar', allRoutes: 'Barcha marshrutlar', more: 'KO\'PROQ', scanTitle: 'Interaktiv gid', scanSubheader: 'Eksponatlarni kamera yordamida tanib oling', nearbyExhibits: 'Yaqin atrofdagi eksponatlar', catalog: 'Katalog', language: 'Til', navRecommend: 'Tavsiya', navInMuseum: 'Muzeydaman', navCatalog: 'Katalog', navProfile: 'Profil', scanButtonText: 'Eksponatni skanerlash', popupTitle: 'Rasm manbasi', popupMessage: 'Rasmni qanday olishni xohlaysiz?', popupCamera: 'Suratga olish', popupGallery: 'Galeriyadan tanlash', wipSubtitle: 'Ushbu bo\'lim tez orada paydo bo\'ladi', loadingError: 'Yuklab bo\'lmadi', newsError: 'Yangiliklar topilmadi', themeLabel: "Qorong'u rejim", themeLabelDark: "Qorong'u rejim", themeLabelLight: 'Yorug\' rejim', aiContext: "Tarixiy kontekst", aiFact: "Qizqarli fakt", periodLabel: 'Davr:', descriptionLabel: 'Tavsif:', contextLabel: 'Tarixiy ma‘lumot:', factLabel: 'Qiziqarli fakt:'},
        en: { exhibitions: 'Exhibitions', navImmersion: 'Immersion', museums: 'Museums', routes: 'Routes', allExhibitions: 'All Exhibitions', allMuseums: 'All Museums', allRoutes: 'All Routes', more: 'MORE', scanTitle: 'Interactive Guide', scanSubheader: 'Recognize exhibits using your camera', nearbyExhibits: 'Exhibits Nearby', catalog: 'Catalog', language: 'Language', navRecommend: 'Recommends', navInMuseum: 'In Museum', navCatalog: 'Catalog', navProfile: 'Profile', scanButtonText: 'Scan Exhibit', popupTitle: 'Photo Source', popupMessage: 'How would you like to get the image?', popupCamera: 'Take Photo', popupGallery: 'Choose from Gallery', wipSubtitle: 'This section will appear soon!', loadingError: 'Failed to load', newsError: 'News not found', themeLabel: 'Dark Mode', themeLabelDark: 'Dark Mode', themeLabelLight: 'Light Mode', aiContext: "Historical Context", aiFact: "Interesting Fact", },
    };
    let currentLanguage = 'ru';

    const setLanguage = (lang, shouldReloadContent = false) => {
        currentLanguage = translations[lang] ? lang : 'ru';
        document.querySelectorAll('[data-lang-key]').forEach(element => {
            const key = element.getAttribute('data-lang-key');
            if (translations[currentLanguage][key]) element.textContent = translations[currentLanguage][key];
        });
        localStorage.setItem('userLanguage', currentLanguage);
        document.querySelectorAll('.lang-button').forEach(btn => btn.classList.toggle('active', btn.dataset.lang === currentLanguage));
        document.documentElement.lang = currentLanguage;
        if (shouldReloadContent) {
            loadNews(); loadExhibitions(); loadMuseums(); loadRoutes();
            loadCatalogItems('cities', 'cities-grid-container');
            loadCatalogItems('sights', 'sights-grid-container');
            loadCatalogItems('cuisine', 'cuisine-grid-container');
        }
    };

    const initLanguage = () => {
        const savedLang = localStorage.getItem('userLanguage') || navigator.language.slice(0, 2) || 'ru';
        setLanguage(savedLang, false);
        document.querySelectorAll('.lang-button').forEach(btn => {
            btn.addEventListener('click', () => {
                if (currentLanguage !== btn.dataset.lang) setLanguage(btn.dataset.lang, true);
                if (tg && tg.HapticFeedback) tg.HapticFeedback.impactOccurred('light');
            });
        });
    };
    
    // ===============================================
    // --- РЕНДЕРИНГ И ЗАГРУЗКА ДАННЫХ ---
    // ===============================================
    
    const createGenericCard = (item, isGrid = false) => {
        const imageUrl = item.image_url || 'https://via.placeholder.com/160x100?text=No+Image';
        const descriptionParts = [];
        if (item.date_range) descriptionParts.push(item.date_range);
        if (item.location) descriptionParts.push(item.location);
        const description = descriptionParts.join(' • ');
        const cardElement = document.createElement(isGrid ? 'div' : 'a');
        cardElement.className = 'card' + (isGrid ? ' grid-item' : '');
        if (!isGrid) { cardElement.href = item.url || '#'; cardElement.target = '_blank'; }
        cardElement.innerHTML = `<img src="${imageUrl}" class="card-image" alt="${item.title}"><div class="card-body"><h3 class="card-title">${item.title || 'Без названия'}</h3>${description ? `<p class="card-description">${description}</p>` : ''}</div>`;
        return cardElement;
    };

    const createNewsSlide = (news, index) => {
        const slide = document.createElement('div');
        slide.className = 'carousel-slide';
        if (index === 0) slide.classList.add('active');
        slide.style.backgroundImage = `url('${news.image_url}')`;
        slide.innerHTML = `<div class="hero-content"><p class="hero-subtitle">${new Date(news.date).toLocaleDateString()}</p><h1 class="hero-title">${news.title}</h1></div>`;
        return slide;
    };
    
    const createRouteCard = (item, isGrid = false) => {
        const imageUrl = item.image_url || 'https://via.placeholder.com/280x150?text=No+Image';
        const cardClass = isGrid ? 'card-wide grid-item' : 'card-wide';
        const cardElement = document.createElement('a');
        cardElement.className = cardClass;
        cardElement.href = item.url || '#';
        cardElement.target = '_blank';
        cardElement.innerHTML = `<img src="${imageUrl}" class="card-image" alt="${item.title}"><div class="card-body"><h3 class="card-title">${item.title || 'Без названия'}</h3></div>`;
        return cardElement;
    };

    const renderError = (container, key) => { if(container) container.innerHTML = `<p class="error-message">${translations[currentLanguage][key] || "Error"}</p>`; };

    const renderSkeletons = (container, count = 4, isWide = false) => {
        if (!container) return;
        container.innerHTML = '';
        for (let i = 0; i < count; i++) {
            const skeleton = document.createElement('div');
            skeleton.className = isWide ? 'card-wide skeleton' : 'card skeleton';
            if (!isWide) skeleton.innerHTML = `<div class="card-image"></div><div class="card-body"></div>`;
            container.appendChild(skeleton);
        }
    };
    
    const loadNews = async () => {
        const carousel = document.getElementById('news-carousel');
        if(!carousel) return;
        renderSkeletons(carousel, 1, true);
        try {
            const response = await fetch(`/api/news?lang=${currentLanguage}`);
            if (!response.ok) throw new Error('HTTP error');
            const newsData = await response.json();
            if (!newsData || newsData.length === 0) throw new Error('newsError');
            carousel.innerHTML = '';
            newsData.forEach((news, index) => carousel.appendChild(createNewsSlide(news, index)));
            let currentSlide = 0;
            const slides = carousel.querySelectorAll('.carousel-slide');
            if (slides.length <= 1) return;
            if (window.newsInterval) clearInterval(window.newsInterval);
            window.newsInterval = setInterval(() => {
                currentSlide = (currentSlide + 1) % slides.length;
                slides.forEach((slide, i) => slide.classList.toggle('active', i === currentSlide));
                if (tg && tg.HapticFeedback) tg.HapticFeedback.impactOccurred('light');
            }, 7000);
        } catch (error) { console.error('Ошибка загрузки новостей:', error.message); renderError(carousel, 'newsError'); }
    };

    const loadExhibitions = async () => {
        const scrollContainer = document.getElementById('exhibitions-container');
        const gridContainer = document.getElementById('all-exhibitions-grid-container');
        if(scrollContainer) renderSkeletons(scrollContainer, 4, false);
        if(gridContainer) renderSkeletons(gridContainer, 8, false);
        try {
            const response = await fetch(`/api/exhibitions?lang=${currentLanguage}`);
            if (!response.ok) throw new Error('HTTP error');
            const data = await response.json();
            if (data.error || !Array.isArray(data) || data.length === 0) throw new Error('loadingError');
            if(scrollContainer) scrollContainer.innerHTML = '';
            if(gridContainer) gridContainer.innerHTML = '';
            if(scrollContainer) data.slice(0, 4).forEach(ex => scrollContainer.appendChild(createGenericCard(ex, false)));
            if(gridContainer) data.forEach((ex, i) => {
                const card = createGenericCard(ex, true);
                card.style.animationDelay = `${i * 50}ms`;
                gridContainer.appendChild(card);
            });
        } catch (error) { console.error('Ошибка загрузки выставок:', error.message); if(scrollContainer) renderError(scrollContainer, 'loadingError'); if(gridContainer) renderError(gridContainer, 'loadingError'); }
    };

    const loadMuseums = async () => {
        const scrollContainer = document.getElementById('museums-container');
        const gridContainer = document.getElementById('all-museums-grid-container');
        if(scrollContainer) renderSkeletons(scrollContainer, 4, false);
        if(gridContainer) renderSkeletons(gridContainer, 8, false);
        try {
            const response = await fetch(`/api/museums?lang=${currentLanguage}`);
            if (!response.ok) throw new Error('HTTP error');
            const data = await response.json();
            if (data.error || !Array.isArray(data) || data.length === 0) throw new Error('loadingError');
            if(scrollContainer) scrollContainer.innerHTML = '';
            if(gridContainer) gridContainer.innerHTML = '';
            if(scrollContainer) data.slice(0, 4).forEach(museum => scrollContainer.appendChild(createGenericCard(museum, false)));
            if(gridContainer) data.forEach((museum, i) => {
                const card = createGenericCard(museum, true);
                card.style.animationDelay = `${i * 50}ms`;
                gridContainer.appendChild(card);
            });
        } catch (error) { console.error('Ошибка загрузки музеев:', error.message); if(scrollContainer) renderError(scrollContainer, 'loadingError'); if(gridContainer) renderError(gridContainer, 'loadingError'); }
    };
    
    const loadRoutes = async () => {
        const scrollContainer = document.getElementById('routes-container');
        const gridContainer = document.getElementById('all-routes-grid-container');
        if(scrollContainer) renderSkeletons(scrollContainer, 3, true);
        if(gridContainer) renderSkeletons(gridContainer, 8, true);
        try {
            const response = await fetch(`/api/routes?lang=${currentLanguage}`);
            if (!response.ok) throw new Error('HTTP error');
            const data = await response.json();
            if (data.error || !Array.isArray(data) || data.length === 0) throw new Error('loadingError');
            if(scrollContainer) scrollContainer.innerHTML = '';
            if(gridContainer) gridContainer.innerHTML = '';
            if(scrollContainer) data.slice(0, 4).forEach(route => scrollContainer.appendChild(createRouteCard(route)));
            if(gridContainer) data.forEach((route, i) => {
                const card = createRouteCard(route, true);
                card.style.animationDelay = `${i * 50}ms`;
                gridContainer.appendChild(card);
            });
        } catch (error) { console.error('Ошибка загрузки маршрутов:', error.message); if(scrollContainer) renderError(scrollContainer, 'loadingError'); if(gridContainer) renderError(gridContainer, 'loadingError'); }
    };

    const loadCatalogItems = async (category, containerId) => {
        const gridContainer = document.getElementById(containerId);
        if (!gridContainer) return;
        renderSkeletons(gridContainer, 8, false);
        try {
            const response = await fetch(`/api/catalog?lang=${currentLanguage}&category=${category}`);
            if (!response.ok) throw new Error('HTTP error');
            const data = await response.json();
            if (data.error || !Array.isArray(data) || data.length === 0) { throw new Error('loadingError'); }
            gridContainer.innerHTML = '';
            data.forEach((item, i) => {
                const card = createGenericCard(item, true);
                card.style.animationDelay = `${i * 50}ms`;
                gridContainer.appendChild(card);
            });
        } catch (error) { console.error(`Ошибка загрузки каталога (${category}):`, error.message); renderError(gridContainer, 'loadingError'); }
    };
    
    
    
    const handlePhoto = async (photoData) => {
        switchPage('page-scan-result');
        const resultImage = document.getElementById('result-image');
        const resultTextContainer = document.getElementById('result-text');
        const skeleton = document.getElementById('result-text-skeleton');

        const imageUrl = URL.createObjectURL(photoData);
        if (resultImage) resultImage.src = imageUrl;

        if (resultTextContainer) resultTextContainer.style.display = 'none';
        if (skeleton) skeleton.style.display = 'block';

        const reader = new FileReader();
        reader.readAsDataURL(photoData);
        reader.onloadend = async () => {
            const base64Image = reader.result.split(',')[1];
            try {
                const response = await fetch('/api/analyze-image', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ image: base64Image, lang: currentLanguage })
                });
                if (!response.ok) throw new Error('Server error');
                
                // Получаем JSON, в котором есть ключ 'description' с нашим HTML
                const data = await response.json();
                
                if (skeleton) skeleton.style.display = 'none';
                
                if (resultTextContainer) {
                    // *** ГЛАВНОЕ: Просто вставляем готовый HTML, который прислал бэкенд ***
                    resultTextContainer.innerHTML = data.description || `<p>${translations[currentLanguage].loadingError}</p>`;
                    resultTextContainer.style.display = 'block';
                }

            } catch (error) {
                console.error('Ошибка анализа фото:', error);
                if (skeleton) skeleton.style.display = 'none';
                if (resultTextContainer) {
                    renderError(resultTextContainer, 'loadingError');
                    resultTextContainer.style.display = 'block';
                }
            }
        };
    };
    
    const triggerFileInput = (useCapture) => {
        const fileInput = document.createElement('input');
        fileInput.type = 'file';
        fileInput.accept = 'image/*';
        if (useCapture) { fileInput.capture = 'environment'; }
        fileInput.onchange = (e) => {
            const file = e.target.files[0];
            if (file) handlePhoto(file);
        };
        fileInput.click();
    };
    
    // === ЛОГИКА НАВИГАЦИИ И UI ===
    const switchPage = (targetId) => {
        if (!targetId) return;
        const currentActivePage = document.querySelector('.page.active');
        const newActivePage = document.getElementById(targetId);
        if (currentActivePage && currentActivePage.id === targetId) return;
        pages.forEach(page => page.classList.remove('active'));
        if (newActivePage) newActivePage.classList.add('active');
        navItems.forEach(navItem => {
            navItem.classList.toggle('active', navItem.dataset.target === targetId);
        });
        appContainer.scrollTo(0, 0);
        if (tg && tg.HapticFeedback) tg.HapticFeedback.impactOccurred('light');
        if (tg && tg.BackButton) {
            const isHomePage = targetId === 'page-home';
            const isCatalogPage = targetId === 'page-catalog';
            if (isHomePage || isCatalogPage) {
                tg.BackButton.hide();
            } else {
                tg.BackButton.show();
            }
        }
    };

    const setupEventListeners = () => {
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const targetId = link.dataset.target;
                if (targetId) switchPage(targetId);
            });
        });
        document.querySelectorAll('.catalog-menu-item.wip').forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                if (tg && tg.showAlert) tg.showAlert(translations[currentLanguage].wipSubtitle);
            });
        });
        
        document.getElementById('theme-toggle-checkbox')?.addEventListener('change', e => {
            applyTheme(e.target.checked ? 'dark' : 'light');
        });
        
        const scanActionButton = document.getElementById('scan-action-button');
        if (scanActionButton) {
            scanActionButton.addEventListener('click', () => {
                if (tg && tg.showPopup) {
                    tg.showPopup({
                        title: translations[currentLanguage].popupTitle,
                        message: translations[currentLanguage].popupMessage,
                        buttons: [
                            { id: 'camera', type: 'default', text: translations[currentLanguage].popupCamera },
                            { id: 'gallery', type: 'default', text: translations[currentLanguage].popupGallery },
                            { type: 'cancel' }
                        ]
                    }, (buttonId) => {
                        if (buttonId === 'camera') {
                            triggerFileInput(true);
                        } else if (buttonId === 'gallery') {
                            triggerFileInput(false);
                        }
                    });
                } else {
                    triggerFileInput(true);
                }
            });
        }
        
        // **ВОССТАНОВЛЕННЫЙ ОБРАБОТЧИК КНОПКИ "НАЗАД"**
        if (tg && tg.BackButton) {
            tg.BackButton.onClick(() => {
                const currentPage = document.querySelector('.page.active');
                if (!currentPage) { switchPage('page-home'); return; }

                const isSubPageOfHome = ['page-all-exhibitions', 'page-all-museums', 'page-all-routes'].includes(currentPage.id);
                const isSubPageOfCatalog = ['page-cities', 'page-sights', 'page-cuisine', 'page-favorites'].includes(currentPage.id);
                const isScanResult = currentPage.id === 'page-scan-result';
                
                if (isScanResult) switchPage('page-scan');
                else if (isSubPageOfCatalog) switchPage('page-catalog');
                else if (isSubPageOfHome) switchPage('page-home');
                else if (currentPage.id === 'page-profile') switchPage('page-home');
                else switchPage('page-home');
            });
        }
    };
    
    // === УПРАВЛЕНИЕ ТЕМАМИ ===
    const applyTheme = (theme) => {
        document.body.dataset.theme = theme;
        localStorage.setItem('appTheme', theme);
        const isDark = theme === 'dark';
        const themeCheckbox = document.querySelector('#theme-toggle-checkbox');
        if (themeCheckbox) {
            themeCheckbox.checked = isDark;
        }
        if (tg) {
            const bgColor = isDark ? '#101014' : '#F8F5EF';
            tg.setHeaderColor(bgColor);
            tg.setBackgroundColor(bgColor);
        }
        const themeLabel = document.querySelector('.theme-toggle-label');
        if (themeLabel && translations[currentLanguage]) {
            themeLabel.textContent = translations[currentLanguage][isDark ? 'themeLabelDark' : 'themeLabelLight'];
        }
    };
    
    const initProfile = () => {
        const user = tg?.initDataUnsafe?.user;
        const profileName = document.querySelector('.profile-name');
        const profileUsername = document.querySelector('.profile-username');
        if (profileName) profileName.textContent = user ? `${user.first_name || ''} ${user.last_name || ''}`.trim() || 'Guest' : 'Guest';
        if (profileUsername) profileUsername.textContent = user?.username ? `@${user.username}` : '';
    };

    // ===============================================
    // --- ГЛАВНАЯ ТОЧКА ВХОДА ---
    // ===============================================
    (() => {
        if (tg && tg.BackButton) tg.BackButton.hide();
        
        const savedTheme = localStorage.getItem('appTheme') || 'dark'; // Темная тема по умолчанию
        applyTheme(savedTheme);
        setSpacerHeight();
        initLanguage();
        setupEventListeners();
        
        loadNews();
        loadExhibitions();
        loadMuseums();
        loadRoutes();
        loadCatalogItems('cities', 'cities-grid-container');
        loadCatalogItems('sights', 'sights-grid-container');
        loadCatalogItems('cuisine', 'cuisine-grid-container');
        
        initProfile();
        
        // **ГЛАВНОЕ ИСПРАВЛЕНИЕ: НАДЕЖНАЯ ПРОВЕРКА ПАРАМЕТРА**
        // Мы проверяем и `start_param`, и hash в URL. Что-то одно точно сработает.
        const startParam = tg?.initDataUnsafe?.start_param;
        const hashParam = window.location.hash.substring(1);
        
        const artifactId = startParam || hashParam;

        if (artifactId && videoDatabase[artifactId]) {
            console.log(`Обнаружен deep link: ${artifactId}. Запускаю видео...`);
            
            // Запускаем видео с небольшой задержкой, чтобы интерфейс успел отрисоваться
            // Это также помогает избежать проблем с автопроигрыванием в некоторых браузерах
            setTimeout(() => {
                showVideoModal(artifactId);
            }, 500); // 0.5 секунды
            
        } else {
            // Если параметра нет, просто показываем главную страницу
            switchPage('page-home');
        }

        // Настройки, которые зависят от Telegram API
        if (tg) {
            tg.BackButton.hide();
            window.addEventListener('resize', setSpacerHeight);
            setSpacerHeight();
        }
    })();
});