// Form submission handler
const addProductBtn = document.querySelector('button[type="submit"]');
addProductBtn.addEventListener('click', async function(event) {
    event.preventDefault();

    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    if (!csrfToken) {
        showToast('CSRF Token not found!');
        console.error('CSRF token not found!');
        return;
    }
    
    const category = document.getElementById('product-category').value;
    const models = document.getElementById('model-number').value;
    
    if (!category) {
        showToast('Please select product category.');
        return;
    }
    if (!models) {
        showToast('Please enter product model number.');
        return;
    }

    addProductBtn.disabled = true;
    addProductBtn.querySelector('span').textContent = 'Creating...';

    const productModels = models.split(';').map(model => model.trim()).filter(model => model !== "");
    await Promise.all(
        productModels.map(async (model) => {
            try {
                const response = await fetch(`/product/create/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken,
                    },
                    body: JSON.stringify({
                        category: category,
                        model: model
                    }),
                });
        
                const result = await response.json();
        
                if (result.status === 'success') {
                    showToast("Success: " + result.message);
                    insertProductIntoTable(result.data);
                } else {
                    showToast("Error: " + result.message);
                }
            } catch (error) {
                console.error('Error:' + error);
                showToast('An error occurred while adding product.');
            }
        })
    );

    document.getElementById('product-category').value = "";
    document.getElementById('model-number').value = "";
    
    addProductBtn.disabled = false;
    addProductBtn.querySelector('span').textContent = 'Add Product';
});


function insertProductIntoTable(product={}) {
    if (!product) {
        return;
    }

    const productHTML = `
        <tr class="product-item">
            <td class="px-6 py-4 whitespace-nowrap">
                <span class="px-2 inline-flex text-xs leading-5 font-medium rounded-full text-gray-100">${product.category}</span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-100">${product.model}</td>
            
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-400">
                <button class="text-blue-400 hover:text-blue-300 mr-3"><i class="fas fa-edit"></i></button>
                <button class="text-red-400 hover:text-red-300"><i class="fas fa-trash"></i></button>
            </td>
        </tr>
    `;

    const tableBody = document.getElementById('product-table-body');
    tableBody.insertAdjacentHTML('beforeend', productHTML);
}





// Sorting functionality
let currentSort = {
    field: 'category',
    direction: 'asc'
};

const sortHeaders = document.querySelectorAll('.sort-header');
sortHeaders.forEach(header => {
    header.addEventListener('click', () => {
        const field = header.dataset.sort;
        
        // Toggle sort direction if clicking the same field
        if (currentSort.field === field) {
            currentSort.direction = currentSort.direction === 'asc' ? 'desc' : 'asc';
        } else {
            currentSort.field = field;
            currentSort.direction = 'asc';
        }

        // Update sort icons
        sortHeaders.forEach(h => {
            const icon = h.querySelector('.sort-icon');
            if (h.dataset.sort === currentSort.field) {
                icon.className = currentSort.direction === 'asc' 
                    ? 'fas fa-sort-up sort-icon ml-2 text-blue-400' 
                    : 'fas fa-sort-down sort-icon ml-2 text-blue-400';
            } else {
                icon.className = 'fas fa-sort sort-icon ml-2 text-gray-400';
            }
        });

        // Sort the table (in a real app, you would fetch sorted data from the server)
        sortTable();
    });
});

// Sort dropdown handler
document.getElementById('sort-by').addEventListener('change', function() {
    const [field, direction] = this.value.split('-');
    currentSort = { field, direction };
    sortTable();
});

function sortTable() {
    const rows = Array.from(document.querySelectorAll('#product-table-body tr'));
    
    rows.sort((a, b) => {
        const aValue = a.querySelector(`td:nth-child(${currentSort.field === 'category' ? 1 : 2})`).textContent;
        const bValue = b.querySelector(`td:nth-child(${currentSort.field === 'category' ? 1 : 2})`).textContent;
        
        if (aValue < bValue) return currentSort.direction === 'asc' ? -1 : 1;
        if (aValue > bValue) return currentSort.direction === 'asc' ? 1 : -1;
        return 0;
    });

    const tableBody = document.getElementById('product-table-body');
    tableBody.innerHTML = '';
    rows.forEach(row => tableBody.appendChild(row));
}
