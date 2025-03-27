let AccountData = [];

// DOM References
const DOM = {
    query: document.getElementById('searchField'), // Input field
    filterBy: document.getElementById('filterField'), // Dropdown select
    dataList: document.getElementById('dataList'), // Data container
    loadingState: document.getElementById('loadingState'),
    emptyState: document.getElementById('emptyState'),
    errorState: document.getElementById('errorState')
};

// Render Data Function
const renderData = (data) => {
    DOM.dataList.innerHTML = data.map((item, index) => `
        <a href="/account/get/${item.pk}/" class="data-item grid grid-cols-3 md:grid-cols-6 gap-4 items-center px-6 py-2 hover:bg-gray-700/20 transition-all" 
           style="animation-delay: ${index * 50}ms">
            <div class="col-span-2 flex items-center gap-4">
                <img src="${item.avatar}" class="w-10 h-10 rounded-full">
                <div>
                    <h3 class="font-medium">${item.name}</h3>
                    <span class="text-xs ${item.isActive === true ? 'text-green-400' : 'text-gray-400'}">
                        ${item.isActive === true ? 'Active' : 'Closed'}
                    </span>
                </div>
            </div>
            <div class="hidden md:block md:col-span-2 text-gray-400">${item.phone}</div>
            <div class="font-mono text-sm">${item.account}</div>
            <div class="hidden md:block text-right font-medium ${item.balance < 0 ? 'text-red-400' : 'text-blue-400'}">
                ${item.balance}
            </div>
        </a>
    `).join('');

    DOM.emptyState.classList.toggle('hidden', data.length > 0);
    DOM.dataList.classList.toggle('hidden', data.length === 0);
};

// Filter Data Function
const filterData = () => {
    const queryText = DOM.query.value.toLowerCase();
    const filterBy = DOM.filterBy.value;

    const filtered = AccountData.filter(item => 
        String(item[filterBy]).toLowerCase().includes(queryText)
    );

    renderData(filtered);
};

// Initialize Data Function
const init = async () => {
    try {
        DOM.loadingState.classList.remove('hidden');
        DOM.errorState.classList.add('hidden');
        DOM.dataList.classList.add('hidden');

        // Simulated API call with dummy data
        // await new Promise(resolve => setTimeout(resolve, 200));
        // AccountData = [
        //     {
        //         name: "John Doe",
        //         phone: "+880 1712-000000",
        //         account: "ID-123456",
        //         balance: 5000,
        //         avatar: "https://via.placeholder.com/40",
        //         isActive: true
        //     },
        // ];

        // Fetch data from the backend
        const response = await fetch('/accounts/get/');
        if (!response.ok) throw new Error('Server response error');
        const data = await response.json();
        

        if (data.success) {
            AccountData = data.accounts;
            renderData(AccountData);
        } else {
            DOM.emptyState.classList.remove('hidden');
        }

    } catch (err) {
        console.error('Data initialization error:', err);
        DOM.errorState.classList.remove('hidden');
    } finally {
        DOM.loadingState.classList.add('hidden');
    }
};

// Event Listeners
DOM.query.addEventListener('input', filterData);
DOM.filterBy.addEventListener('change', filterData);

// Start Application
DOM.query.focus();
init();