let AccDetilsDOM = {
    newPaymentForm: document.getElementById('newPaymentForm'),

    paymentAmount: document.getElementById('paymentAmount'),
    receiptNumber: document.getElementById('receiptNumber'),
    paymentDate: document.getElementById('paymentDate'),

    paymentSubmitBtn: document.getElementById('paymentSubmitBtn'),
}

AccDetilsDOM.paymentSubmitBtn.addEventListener('click', () => {
    createNewPayment();
});

// Submit Form
async function createNewPayment() {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
    if (!csrfToken) {
        console.error('CSRF token not found!');
        return;
    }

    const formData = {
        paymentAmount: AccDetilsDOM.paymentAmount.value,
        receiptNumber: AccDetilsDOM.receiptNumber.value,
        paymentDate: AccDetilsDOM.paymentDate.value,
    }

    console.log(formData);
    // Validate form data
    for (const [key, value] of Object.entries(formData)) {
        if (!value) {
            showToast(`Please fill in the "${key}" field.`);
            return;
        }
    }

    const account = document.getElementById('accountNumber').textContent;
    try {
        const response = await fetch('/account/get/${account}/make-payment/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
            },
            body: JSON.stringify(formData),
        });

        const result = await response.json();

        if (result.status === 'success') {
            showToast("Success: " + result.message);
            console.log(result.payment);

        } else {
            showToast("Error: " + result.message);
        }
    } catch (error) {
        console.error('Error:', error);
        showToast('An error occurred while creating the account.');
    } finally {
        toggleModal(false);
    }
}



// set default date in payment modal input
const today = new Date().toLocaleDateString('en-CA'); // 'en-CA' gives YYYY-MM-DD format
AccDetilsDOM.paymentDate.value = today;
AccDetilsDOM.paymentDate.max = today;



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
