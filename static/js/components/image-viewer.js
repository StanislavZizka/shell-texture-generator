document.addEventListener("DOMContentLoaded", function () {
    const popup = document.getElementById("popupContainer");
    if (popup) {
        popup.style.display = "none";
    }
    
    // Global variables for drag and zoom functionality
    let currentScale = 1;
    let currentX = 0;
    let currentY = 0;
    let isDragging = false;
    let dragStartX = 0;
    let dragStartY = 0;
    
    function updateTransform(img) {
        img.style.transform = `translate(${currentX}px, ${currentY}px) scale(${currentScale})`;
    }
    
    function resetTransform(img) {
        currentScale = 1;
        currentX = 0;
        currentY = 0;
        updateTransform(img);
    }
    
    // Add double-click zoom for desktop
    document.addEventListener('dblclick', function(e) {
        const popup = document.getElementById("popupContainer");
        if (!popup || popup.style.display === "none") return;
        
        const popupImg = document.getElementById("popupImage");
        if (popupImg && e.target === popupImg) {
            if (currentScale > 1) {
                resetTransform(popupImg);
                popupImg.classList.remove('zoomed');
                popup.classList.remove('zoomed');
            } else {
                currentScale = 2;
                updateTransform(popupImg);
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
            
            const delta = e.deltaY > 0 ? 0.9 : 1.1;
            currentScale = Math.min(Math.max(0.5, currentScale * delta), 4);
            
            // Reset position when zooming out to 1x or less
            if (currentScale <= 1) {
                currentX = 0;
                currentY = 0;
            }
            
            updateTransform(popupImg);
            
            if (currentScale > 1) {
                popupImg.classList.add('zoomed');
                popup.classList.add('zoomed');
            } else {
                popupImg.classList.remove('zoomed');
                popup.classList.remove('zoomed');
            }
        }
    });
    
    // Mouse drag functionality
    document.addEventListener('mousedown', function(e) {
        const popup = document.getElementById("popupContainer");
        if (!popup || popup.style.display === "none") return;
        
        const popupImg = document.getElementById("popupImage");
        if (popupImg && e.target === popupImg && currentScale > 1) {
            isDragging = true;
            dragStartX = e.clientX - currentX;
            dragStartY = e.clientY - currentY;
            e.preventDefault();
        }
    });
    
    document.addEventListener('mousemove', function(e) {
        if (!isDragging) return;
        
        const popupImg = document.getElementById("popupImage");
        if (popupImg) {
            currentX = e.clientX - dragStartX;
            currentY = e.clientY - dragStartY;
            updateTransform(popupImg);
        }
    });
    
    document.addEventListener('mouseup', function() {
        isDragging = false;
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
        currentScale = 1;
        currentX = 0;
        currentY = 0;
        popupImg.style.transform = 'translate(0px, 0px) scale(1)';
        popupImg.classList.remove('zoomed');
        popup.classList.remove('zoomed');
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
        
        // Clear popup image and reset zoom state
        const popupImg = document.getElementById("popupImage");
        if (popupImg) {
            popupImg.src = '';
            popupImg.style.opacity = '1';
            popupImg.style.transform = 'translate(0px, 0px) scale(1)';
            popupImg.classList.remove('zoomed');
        }
        
        // Reset global zoom state
        currentScale = 1;
        currentX = 0;
        currentY = 0;
        isDragging = false;
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
            const popup = document.getElementById("popupContainer");
            if (popupImg) {
                currentScale = Math.min(Math.max(0.5, scale), 3); // Limit zoom
                
                // Reset position when scaling down
                if (currentScale <= 1) {
                    currentX = 0;
                    currentY = 0;
                }
                
                updateTransform(popupImg);
                
                // Update classes
                if (currentScale > 1) {
                    popupImg.classList.add('zoomed');
                    if (popup) popup.classList.add('zoomed');
                } else {
                    popupImg.classList.remove('zoomed');
                    if (popup) popup.classList.remove('zoomed');
                }
            }
        }
    }
});
