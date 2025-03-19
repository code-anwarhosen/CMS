// Function to toggle sections
function toggleSection(sectionId) {
    const section = document.getElementById(sectionId);
    const icon = document.getElementById(`${sectionId}Icon`);

    section.classList.toggle('hidden');
    icon.classList.toggle('fa-plus');
    icon.classList.toggle('fa-minus');
}

// Optional: Open all sections by default on page load
window.addEventListener('load', () => {
    const sections = ['customerInfo', 'guarantorDetails', 'contractTerms', 'productDetails', 'paymentSchedule'];
    sections.forEach(sectionId => {
        toggleSection(sectionId); // Open all sections
    });
});




// =========== Handles payment modal =====================
const modal = document.getElementById('paymentModal');
const openBtn = document.getElementById('openPaymentModal');
const closeBtns = document.querySelectorAll('#closeModal, #cancelModal');

// Modal Animation Handling
function toggleModal(show) {
    if(show) {
        modal.classList.remove('hidden');
        modal.classList.add('flex');
        modal.children[0].style.animation = 'paymentModalIn 0.4s ease-in';
    } else {
        modal.children[0].style.animation = 'paymentModalOut 0.3s ease-out';
        setTimeout(() => modal.classList.add('hidden'), 300);
        setTimeout(() => modal.classList.remove('flex'), 300);
    }
}

// Event Listeners
openBtn.addEventListener('click', () => toggleModal(true));
closeBtns.forEach(btn => btn.addEventListener('click', () => toggleModal(false)));
modal.addEventListener('click', (e) => e.target === modal && toggleModal(false));
document.addEventListener('keydown', (e) => e.key === 'Escape' && toggleModal(false));
