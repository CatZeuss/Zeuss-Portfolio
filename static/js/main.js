// Función global para pre-llenar el formulario de contacto
function presetContactForm(title, message) {
    const subjectInput = document.querySelector('#subject');
    const messageInput = document.querySelector('#message');

    if (subjectInput) {
        subjectInput.value = `Quero pedir um ${title}`;
    }

    if (messageInput) {
        messageInput.value = message;
    }
}

document.addEventListener('DOMContentLoaded', function() {
    // Smooth scroll for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Intersection Observer for scroll animations
    const animateOnScrollElements = document.querySelectorAll('.animate-on-scroll');

    const observerOptions = {
        threshold: 0.15,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                // Add random delay for staggered animation effect
                entry.target.style.transitionDelay = `${Math.random() * 0.3}s`;
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    animateOnScrollElements.forEach(element => {
        observer.observe(element);
    });

    // Initialize project galleries
    document.querySelectorAll('.project-gallery').forEach(gallery => {
        const container = gallery.querySelector('.gallery-container');
        const dots = gallery.querySelectorAll('.gallery-dot');
        const images = gallery.querySelectorAll('img');
        let currentIndex = 0;

        function updateGallery() {
            const offset = -currentIndex * 100;
            container.style.transform = `translateX(${offset}%)`;
            dots.forEach((dot, index) => {
                dot.classList.toggle('active', index === currentIndex);
            });
        }

        function goToSlide(index) {
            const totalSlides = dots.length;
            currentIndex = (index + totalSlides) % totalSlides;
            updateGallery();
        }

        dots.forEach((dot, index) => {
            dot.addEventListener('click', () => goToSlide(index));
        });

        // Initialize fullscreen viewer
        images.forEach((img, index) => {
            img.addEventListener('click', () => {
                showFullscreenImage(images, index);
            });
        });

        // Set initial state
        dots[0]?.classList.add('active');

        // Auto-advance gallery
        let interval;
        function startAutoAdvance() {
            interval = setInterval(() => goToSlide(currentIndex + 1), 5000);
        }
        function stopAutoAdvance() {
            clearInterval(interval);
        }

        gallery.addEventListener('mouseenter', stopAutoAdvance);
        gallery.addEventListener('mouseleave', startAutoAdvance);
        startAutoAdvance();
    });

    // Fullscreen image viewer functionality
    const modal = document.getElementById('fullscreenModal');
    if (modal) {
        const modalImg = modal.querySelector('img');
        const closeModal = document.getElementById('closeModal');
        const prevImage = document.getElementById('prevImage');
        const nextImage = document.getElementById('nextImage');
        let currentImages = [];
        let currentIndex = 0;

        window.showFullscreenImage = function(images, index) {
            currentImages = Array.from(images);
            currentIndex = index;
            updateModalImage();
            modal.classList.remove('hidden');
            modal.classList.add('flex');
        }

        function updateModalImage() {
            modalImg.src = currentImages[currentIndex].src;
            modalImg.alt = currentImages[currentIndex].alt;
        }

        function nextImg() {
            currentIndex = (currentIndex + 1) % currentImages.length;
            updateModalImage();
        }

        function prevImg() {
            currentIndex = (currentIndex - 1 + currentImages.length) % currentImages.length;
            updateModalImage();
        }

        closeModal.addEventListener('click', () => {
            modal.classList.remove('flex');
            modal.classList.add('hidden');
        });

        prevImage.addEventListener('click', prevImg);
        nextImage.addEventListener('click', nextImg);

        // Keyboard navigation
        document.addEventListener('keydown', (e) => {
            if (modal.classList.contains('hidden')) return;

            switch(e.key) {
                case 'Escape':
                    closeModal.click();
                    break;
                case 'ArrowLeft':
                    prevImg();
                    break;
                case 'ArrowRight':
                    nextImg();
                    break;
            }
        });
    }

    // Animate skill progress bars when they come into view
    const progressBars = document.querySelectorAll('.skill-progress');
    const progressObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const progressBar = entry.target.querySelector('.skill-progress-bar');
                const progress = entry.target.getAttribute('data-progress');
                progressBar.style.width = `${progress}%`;
                progressObserver.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.5
    });

    progressBars.forEach(bar => {
        progressObserver.observe(bar);
    });

    // Project filtering
    const filterButtons = document.querySelectorAll('.filter-btn');
    const projectCards = document.querySelectorAll('.project-card');

    filterButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Remove active class from all buttons
            filterButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');

            const filter = button.getAttribute('data-filter');

            projectCards.forEach(card => {
                if (filter === 'all') {
                    card.style.display = '';
                    setTimeout(() => card.style.opacity = '1', 10);
                } else {
                    const technologies = card.getAttribute('data-technologies');
                    if (technologies.includes(filter)) {
                        card.style.display = '';
                        setTimeout(() => card.style.opacity = '1', 10);
                    } else {
                        card.style.opacity = '0';
                        setTimeout(() => card.style.display = 'none', 300);
                    }
                }
            });
        });
    });
});