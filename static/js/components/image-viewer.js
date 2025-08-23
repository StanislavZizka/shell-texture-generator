document.addEventListener("DOMContentLoaded", function () {
    const popup = document.getElementById("popupContainer");
    if (popup) {
        popup.style.display = "none";
    }
    
    // Add double-click zoom for desktop
    document.addEventListener('dblclick', function(e) {
        const popup = document.getElementById("popupContainer");
        if (!popup || popup.style.display === "none") return;
        
        const popupImg = document.getElementById("popupImage");
        if (popupImg && e.target === popupImg) {
            const currentTransform = popupImg.style.transform;
            
            if (currentTransform.includes('scale(2)')) {
                popupImg.style.transform = 'scale(1)';
                popupImg.classList.remove('zoomed');
                popup.classList.remove('zoomed');
            } else {
                popupImg.style.transform = 'scale(2)';
                popupImg.classList.add('zoomed');
                popup.classList.add('zoomed');
            }
        }
    });
    
    // Mouse wheel zoom
    document.addEventListener('wheel', function(e) {
        const popup = document.getElementById("popupContainer");
        if (!popup || popup.style.display === "none") return;
        
        const popupImg = document.getElementById("popupImage");
        if (popupImg && popup.contains(e.target)) {
            e.preventDefault();
            
            const currentTransform = popupImg.style.transform;
            let currentScale = 1;
            
            if (currentTransform.includes('scale(')) {
                const match = currentTransform.match(/scale\(([^)]+)\)/);
                if (match) {
                    currentScale = parseFloat(match[1]);
                }
            }
            
            const delta = e.deltaY > 0 ? 0.9 : 1.1;
            const newScale = Math.min(Math.max(0.5, currentScale * delta), 4);
            
            popupImg.style.transform = `scale(${newScale})`;
            
            if (newScale > 1) {
                popupImg.classList.add('zoomed');
                popup.classList.add('zoomed');
            } else {
                popupImg.classList.remove('zoomed');
                popup.classList.remove('zoomed');
            }
        }
    });
});

function openPopup(imgElement) {
    if (!imgElement || !imgElement.src || imgElement.src.includes('#')) {
        return;
    }
    
    const popup = document.getElementById("popupContainer");
    const popupImg = document.getElementById("popupImage");

    if (popup && popupImg) {
        // Reset zoom and styles first
        popupImg.style.transform = 'scale(1)';
        popupImg.classList.remove('zoomed');
        popupImg.style.opacity = '0.5';
        
        // Set image source
        popupImg.src = imgElement.src;
        
        // Show popup with proper display mode
        popup.style.display = 'block';
        
        // Use timeout to ensure proper layout calculation
        setTimeout(() => {
            popup.classList.add('show');
            popup.classList.add('fade-in');
        }, 10);
        
        // Prevent body scroll when popup is open
        document.body.style.overflow = 'hidden';
        
        // Add loading state for large images
        popupImg.onload = function() {
            this.style.opacity = '1';
            // Force center after image loads
            popup.style.display = 'flex';
        };
        
        // Handle load errors
        popupImg.onerror = function() {
            closePopup();
        };
    }
}

function closePopup(event) {
    const popup = document.getElementById("popupContainer");
    
    if (!popup) return;
    
    // Close on background click, close button, or direct call
    const shouldClose = !event || 
                       event.target.classList.contains("popup") || 
                       event.target.classList.contains("popup-close") ||
                       event.target.closest('.popup-close') ||
                       event.target.querySelector('.fa-times');
    
    if (shouldClose) {
        popup.classList.remove('show');
        popup.classList.remove('fade-in');
        
        // Wait for animation to complete before hiding
        setTimeout(() => {
            popup.style.display = "none";
        }, 300);
        
        // Restore body scroll
        document.body.style.overflow = '';
        
        // Clear popup image
        const popupImg = document.getElementById("popupImage");
        if (popupImg) {
            popupImg.src = '';
            popupImg.style.opacity = '1';
            popupImg.style.transform = 'scale(1)';
            popupImg.classList.remove('zoomed');
        }
    }
}

// Enhanced keyboard navigation
document.addEventListener("keydown", function (event) {
    const popup = document.getElementById("popupContainer");
    if (!popup || popup.style.display === "none") return;
    
    switch(event.key) {
        case "Escape":
            closePopup(event);
            break;
        case "ArrowLeft":
        case "ArrowRight":
            // Future: Add support for image gallery navigation
            break;
    }
});

// Enhanced touch support for mobile
let touchStartY = 0;
let touchStartX = 0;
let isPopupOpen = false;

document.addEventListener('touchstart', function(e) {
    const popup = document.getElementById("popupContainer");
    isPopupOpen = popup && popup.style.display === "flex";
    
    if (isPopupOpen) {
        touchStartY = e.touches[0].clientY;
        touchStartX = e.touches[0].clientX;
        e.preventDefault(); // Prevent scrolling when popup is open
    }
});

document.addEventListener('touchmove', function(e) {
    if (isPopupOpen) {
        e.preventDefault(); // Prevent background scrolling
    }
});

document.addEventListener('touchend', function(e) {
    const popup = document.getElementById("popupContainer");
    if (!popup || popup.style.display === "none") return;
    
    const touchEndY = e.changedTouches[0].clientY;
    const touchEndX = e.changedTouches[0].clientX;
    const diffY = touchStartY - touchEndY;
    const diffX = Math.abs(touchStartX - touchEndX);
    
    // Swipe down to close (minimum 80px vertical, max 50px horizontal)
    if (diffY < -80 && diffX < 50) {
        closePopup(e);
    }
    
    isPopupOpen = false;
});

// Add double-tap to close
let lastTouchTime = 0;
document.addEventListener('touchend', function(e) {
    const popup = document.getElementById("popupContainer");
    if (!popup || popup.style.display === "none") return;
    
    const currentTime = new Date().getTime();
    const tapTime = currentTime - lastTouchTime;
    
    if (tapTime < 500 && tapTime > 0) {
        closePopup(e);
        e.preventDefault();
    }
    
    lastTouchTime = currentTime;
});

// Pinch to zoom support (basic)
let initialDistance = 0;
let currentScale = 1;

document.addEventListener('touchstart', function(e) {
    if (e.touches.length === 2) {
        const touch1 = e.touches[0];
        const touch2 = e.touches[1];
        initialDistance = Math.hypot(
            touch2.clientX - touch1.clientX,
            touch2.clientY - touch1.clientY
        );
    }
});

document.addEventListener('touchmove', function(e) {
    if (e.touches.length === 2) {
        e.preventDefault();
        const touch1 = e.touches[0];
        const touch2 = e.touches[1];
        const currentDistance = Math.hypot(
            touch2.clientX - touch1.clientX,
            touch2.clientY - touch1.clientY
        );
        
        if (initialDistance > 0) {
            const scale = currentDistance / initialDistance;
            const popupImg = document.getElementById("popupImage");
            if (popupImg) {
                currentScale = Math.min(Math.max(0.5, scale), 3); // Limit zoom
                popupImg.style.transform = `scale(${currentScale})`;
            }
        }
    }
});
