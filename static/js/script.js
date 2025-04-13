// Mobile Menu Toggle - navbar
const mobileMenuButton = document.getElementById('mobileMenuButton');
const closeMobileMenu = document.getElementById('closeMobileMenu');
const mobileMenu = document.getElementById('mobileMenu');
const overlay = document.getElementById('overlay');

mobileMenuButton.addEventListener('click', () => {
    mobileMenu.classList.add('active');
    overlay.classList.add('active');
});

closeMobileMenu.addEventListener('click', () => {
    mobileMenu.classList.remove('active');
    overlay.classList.remove('active');
});

overlay.addEventListener('click', () => {
    mobileMenu.classList.remove('active');
    overlay.classList.remove('active');
});
// <<===================== Navbar - END ===========================>>





function setSaleDate(dateInputElement) {
    if (!dateInputElement) return;
    
    const today = new Date().toLocaleDateString('en-CA'); // 'en-CA' gives YYYY-MM-DD format
    dateInputElement.value = today;
    dateInputElement.max = today;
}




function showToast(message, duration = 5000) {
    // Create a <style> element for the CSS
    const style = document.createElement('style');
    style.textContent = `
        .toast-message {
            position: fixed;
            top: 25%; /* Start slightly above the center */
            left: 50%;
            transform: translate(-50%, -50%);
            background-color: rgba(0, 0, 0, 0.8);
            color: white;
            padding: 12px 24px;
            border-radius: 5px;
            box-shadow: 0 4px 8px rgba(50, 50, 50, 0.5);
            z-index: 1000;
            opacity: 0; /* Start invisible */
            transition: opacity 0.5s ease-in-out, top 0.5s ease-in-out;
        }

        .toast-message.show {
            top: 20%; /* Move to the exact center */
            opacity: 1; /* Fully visible */
        }

        .toast-message.hide {
            top: 15%; /* Move slightly above the center */
            opacity: 0; /* Fully invisible */
        }
    `;

    // Append the <style> element to the document's <head>
    document.head.appendChild(style);

    // Create a new div element for the toast
    const toast = document.createElement('div');
    toast.textContent = message;
    toast.classList.add('toast-message');

    // Append the toast to the body
    document.body.appendChild(toast);

    // Trigger the slide-in animation by adding the 'show' class
    setTimeout(() => {
        toast.classList.add('show');
    }, 10); // Small delay to ensure the element is rendered

    // Remove the toast after the specified duration
    setTimeout(() => {
        toast.classList.remove('show'); // Remove the 'show' class
        toast.classList.add('hide'); // Add the 'hide' class for fade-out animation

        // Wait for the fade-out animation to complete
        setTimeout(() => {
            toast.remove(); // Remove the toast from the DOM
            style.remove(); // Remove the dynamically added <style> element
        }, 500); // Match the fade-out animation duration
    }, duration);
}





// Show modal, return true false
function askConfirmation(message, title = "Confirm") {
    return new Promise((resolve) => {
        // Create overlay element
        const overlay = document.createElement('div');
        overlay.className = 'fixed inset-0 bg-black/50 flex items-center justify-center z-50';
        overlay.style.opacity = '0';
        overlay.style.transition = 'opacity 500ms ease';
        
        // Modal HTML template
        overlay.innerHTML = `
            <div class="text-gray-300 bg-gray-800 rounded-lg shadow-lg w-[90vw] sm:w-[350px] max-w-md p-4 transform transition-all duration-200 ease-out translate-y-4 opacity-0">
                <div class="flex justify-between items-center mb-4">
                    <h3 class="text-lg font-semibold text-white">${title}</h3>
                    <button class="hover:text-gray-500 rounded px-2">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="mb-6">${message}</div>

                <div class="flex justify-end gap-2">
                    <button class="px-4 py-2 hover:bg-red-500 rounded">
                        <i class="fas fa-times"></i>
                    </button>
                    <button class="px-4 py-2 bg-gray-700 hover:bg-blue-500 rounded">
                        <i class="fas fa-check"></i>
                    </button>
                </div>
            </div>
        `;
        document.body.appendChild(overlay);
        
        // Force reflow to enable transition
        void overlay.offsetWidth;
        
        // Show overlay and modal
        overlay.style.opacity = '1';
        const modal = overlay.querySelector('div');
        modal.style.opacity = '1';
        modal.style.transform = 'translate-y-0';

        // Close handler
        const closeModal = (result) => {
            // Start fade out animation
            overlay.style.opacity = '0';
            modal.style.opacity = '0';
            modal.style.transform = 'translate-y-4';
            
            // Remove after animation completes
            setTimeout(() => {
                overlay.remove();
                resolve(result);
            }, 300);
        };

        // Get button references
        const [closeBtn, cancelBtn, yesBtn] = overlay.querySelectorAll('button');

        // Event listeners
        closeBtn.onclick = () => closeModal(false);
        cancelBtn.onclick = () => closeModal(false);
        yesBtn.onclick = () => closeModal(true);
        
        // Close when clicking outside modal
        overlay.onclick = (e) => {
            if (e.target === overlay) closeModal(false);
        };

        // Close with Enter/Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') closeModal(true);
            if (e.key === 'Escape') closeModal(false);
        });
    });
}
