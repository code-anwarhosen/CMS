
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


function showToast(message, duration = 5000) {
    // Create a <style> element for the CSS
    const style = document.createElement('style');
    style.textContent = `
        .toast-message {
            position: fixed;
            top: 55%; /* Start slightly below the center */
            left: 50%;
            transform: translate(-50%, -50%);
            background-color: rgba(0, 0, 0, 0.9);
            color: white;
            padding: 12px 24px;
            border-radius: 5px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
            z-index: 1000;
            opacity: 0; /* Start invisible */
            transition: opacity 0.5s ease-in-out, top 0.5s ease-in-out;
        }

        .toast-message.show {
            top: 50%; /* Move to the exact center */
            opacity: 1; /* Fully visible */
        }

        .toast-message.hide {
            top: 45%; /* Move slightly above the center */
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