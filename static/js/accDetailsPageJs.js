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