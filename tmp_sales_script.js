
// Global variables
let searchTimeout;
let saleItemsData = [];
let salePartiesData = [];
console.log('Sales enhanced script v2.1 loaded');

document.addEventListener('DOMContentLoaded', function() {
    console.log('Sales enhanced page init');
    ensureHeaderVisible();
    loadMetaData().then(() => {
        loadSalesTable();
    }).catch(() => loadSalesTable());
    loadStats();
    setTimeout(addActionListeners, 1000);
});

// Load stats on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('Sales enhanced page loaded');
    ensureHeaderVisible();
    loadMetaData();
    loadStats();
    loadSalesTable();
    setTimeout(addActionListeners, 1000);
});

function ensureHeaderVisible() {
    console.log('Ensuring header is visible...');
    const totalElement = document.getElementById('totalSales');
    const monthlyElement = document.getElementById('monthlySales');
    const todayElement = document.getElementById('todaySales');
    
    if (totalElement) { totalElement.textContent = '0'; console.log('Set totalSales to 0'); } else { console.error('totalSales element not found'); }
    if (monthlyElement) { monthlyElement.textContent = '0'; console.log('Set monthlySales to 0'); } else { console.error('monthlySales element not found'); }
    if (todayElement) { todayElement.textContent = '0'; console.log('Set todaySales to 0'); } else { console.error('todaySales element not found'); }
}

// Load stats
function loadStats() {
    console.log('Loading sales stats...');
    
    // Load total sales
    fetch('/api/sales/stats/total')
        .then(response => response.text())
        .then(data => {
            console.log('Total sales:', data);
            document.getElementById('totalSales').textContent = data;
        })
        .catch(error => {
            console.error('Error loading total sales:', error);
            document.getElementById('totalSales').textContent = '0';
        });
    
    // Load monthly sales
    fetch('/api/sales/stats/monthly')
        .then(response => response.text())
        .then(data => {
            console.log('Monthly sales:', data);
            document.getElementById('monthlySales').textContent = data;
        })
        .catch(error => {
            console.error('Error loading monthly sales:', error);
            document.getElementById('monthlySales').textContent = '0';
        });
    
    // Load today's sales
    fetch('/api/sales/stats/today')
        .then(response => response.text())
        .then(data => {
            console.log('Today sales:', data);
            document.getElementById('todaySales').textContent = data;
        })
        .catch(error => {
            console.error('Error loading today sales:', error);
            document.getElementById('todaySales').textContent = '0';
        });
}


async function loadMetaData() {
    try {
        const [partiesRes, itemsRes] = await Promise.all([
            fetch("/api/parties?per_page=500"),
            fetch("/api/items/list")
        ]);
        const partiesData = await partiesRes.json();
        const itemsData = await itemsRes.json();
        if (partiesData.success) {
            salePartiesData = partiesData.parties || [];
            window.salePartiesData = salePartiesData;
            const customerFilter = document.getElementById("customerFilter");
            if (customerFilter) {
                customerFilter.innerHTML = '<option value="">All Customers</option>' +
                    salePartiesData.map(p => `<option value="${p.party_cd}">${p.party_cd} - ${p.party_nm}</option>`).join('');
            }
        }
        if (itemsData.success) {
            saleItemsData = itemsData.items || [];
            window.saleItemsData = saleItemsData;
        }
    } catch (err) {
        console.error("Error loading metadata:", err);
    }
}

async function fetchNextBillNumber() {

    try {
        const res = await fetch('/api/sales/next-bill');
        const data = await res.json();
        return (data.success && data.bill_no) ? data.bill_no : 2001;
    } catch (err) {
        console.error('Error fetching next bill number:', err);
        return 2001;
    }
}

function renderAddSaleModal() {
    const modal = document.getElementById('saleModal');
    if (!modal) return;
    const billDate = new Date().toISOString().split('T')[0];
    const partyOptions = salePartiesData.map(p => `<option value="${p.party_cd}">${p.party_cd} - ${p.party_nm}</option>`).join('');
    const itemsOptions = saleItemsData.map(i => `<option value="${i.it_cd}" data-rate="${i.rate || 0}">${i.it_cd} - ${i.it_nm}</option>`).join('');
    modal.querySelector('.modal-content').innerHTML = `
    <div class="modal-header">
        <h5 class="modal-title" id="saleModalLabel"><i class="fas fa-plus me-2"></i>Add New Sale Bill</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
    </div>
    <div class="modal-body">
        <form id="saleForm" onsubmit="saveSale(event)">
            <div class="row g-3 mb-3">
                <div class="col-md-4">
                    <label class="form-label bright-label">Bill Number</label>
                    <input type="number" class="form-control bright-input" id="sale_bill_no" required>
                </div>
                <div class="col-md-4">
                    <label class="form-label bright-label">Bill Date</label>
                    <input type="date" class="form-control bright-input" id="sale_bill_date" value="${billDate}" required>
                </div>
                <div class="col-md-4">
                    <label class="form-label bright-label">Customer</label>
                    <select class="form-select bright-input" id="sale_party_cd" required>
                        <option value="">Select Customer</option>
                        ${partyOptions}
                    </select>
                </div>
            </div>
            <div class="table-responsive">
                <table class="table table-bordered" id="saleItemsTable">
                    <thead>
                        <tr>
                            <th>Item</th><th>Qty</th><th>Rate</th><th>Discount</th><th>Amount</th><th></th>
                        </tr>
                    </thead>
                    <tbody id="saleItemsTableBody"></tbody>
                </table>
            </div>
            <div class="d-flex justify-content-between mb-3">
                <button type="button" class="btn btn-outline-primary" onclick="addSaleItemRow()"><i class="fas fa-plus me-2"></i>Add Item</button>
                <div class="text-end">
                    <div><small>Sub Total:</small> <input type="number" id="sale_sub_total" class="form-control d-inline-block w-auto" value="0.00" readonly></div>
                    <div><small>Total Discount:</small> <input type="number" id="sale_total_discount" class="form-control d-inline-block w-auto" value="0.00" readonly></div>
                    <div><small>GST (18%):</small> <input type="number" id="sale_gst_amount" class="form-control d-inline-block w-auto" value="0.00" readonly></div>
                    <div><small>Grand Total:</small> <input type="number" id="sale_grand_total" class="form-control d-inline-block w-auto" value="0.00" readonly></div>
                </div>
            </div>
            <div class="text-end">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                <button type="submit" class="btn btn-primary">Save Sale</button>
            </div>
        </form>
    </div>`;
}

// Load sales table
function loadSalesTable() {
    console.log('Loading sales table...');
    const searchTerm = document.getElementById('searchInput').value;
    const dateFilter = document.getElementById('dateFilter') ? document.getElementById('dateFilter').value : '';
    const customerFilter = document.getElementById('customerFilter') ? document.getElementById('customerFilter').value : '';
    const amountFilter = document.getElementById('amountFilter') ? document.getElementById('amountFilter').value : '';
    const sortBy = document.getElementById('sortByFilter') ? document.getElementById('sortByFilter').value : 'date';
    
    const params = new URLSearchParams({ page: 1, per_page: 50 });
    if (searchTerm) params.append('search', searchTerm);
    if (dateFilter) params.append('start_date', dateFilter);
    if (customerFilter) params.append('party_id', customerFilter);
    if (amountFilter) params.append('amount', amountFilter);
    if (sortBy) params.append('sort', sortBy);
    
    fetch(`/api/sales/list?${params.toString()}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                renderSalesTable(data.sales || []);
                const total = data.pagination ? data.pagination.total : (data.sales ? data.sales.length : 0);
                document.getElementById('resultsCount').textContent = `${total} sales loaded`;
            } else {
                document.getElementById('salesTable').innerHTML = '<div class="alert alert-warning mb-0">No sales found</div>';
                document.getElementById('resultsCount').textContent = 'No sales';
            }
        })
        .catch(error => {
            console.error('Error loading sales table:', error);
            document.getElementById('salesTable').innerHTML = '<div class="alert alert-danger mb-0">Error loading sales table</div>';
            document.getElementById('resultsCount').textContent = 'Error loading sales';
        });
}

function renderSalesTable(sales) {
    if (!sales || !sales.length) {
        document.getElementById('salesTable').innerHTML = '<div class="p-3 text-center text-muted">No sales found</div>';
        return;
    }
    let html = `
    <table class="table table-hover mb-0">
        <thead>
            <tr>
                <th>Bill No</th>
                <th>Date</th>
                <th>Customer</th>
                <th>Total Amount</th>
                <th>Status</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody>
    `;
    sales.forEach(sale => {
        const billDate = sale.bill_date ? new Date(sale.bill_date).toLocaleDateString('en-GB') : '-';
        const amount = sale.total_amount ? Number(sale.total_amount).toLocaleString('en-IN', { minimumFractionDigits: 2 }) : '0.00';
        const status = sale.payment_status || 'Pending';
        html += `
            <tr>
                <td><span class="sale-badge">${sale.bill_no || '-'} </span></td>
                <td>${billDate}</td>
                <td>${sale.party_name || sale.party_code || '-'}</td>
                <td>?${amount}</td>
                <td><span class="badge bg-${status === 'Paid' ? 'success' : 'warning'}">${status}</span></td>
                <td>
                    <div class="action-buttons">
                        <button class="btn btn-action btn-view" data-bill-no="${sale.bill_no}" title="View Sale"><i class="fas fa-eye"></i></button>
                        <button class="btn btn-action btn-edit" data-bill-no="${sale.bill_no}" title="Edit Sale"><i class="fas fa-edit"></i></button>
                        <button class="btn btn-action btn-delete" data-bill-no="${sale.bill_no}" title="Delete Sale"><i class="fas fa-trash"></i></button>
                    </div>
                </td>
            </tr>
        `;
    });
    html += '</tbody></table>';
    document.getElementById('salesTable').innerHTML = html;
    addActionListeners();
}

// Add action listeners to buttons
function addActionListeners() {
    console.log('Adding action listeners...');
    
    // Add click listeners to view buttons
    document.querySelectorAll('.btn-view').forEach(button => {
        button.addEventListener('click', function() {
            const billNo = this.getAttribute('data-bill-no');
            console.log('Viewing sale:', billNo);
            openSaleModal(billNo, 'view');
        });
    });
    
    // Add click listeners to edit buttons
    document.querySelectorAll('.btn-edit').forEach(button => {
        button.addEventListener('click', function() {
            const billNo = this.getAttribute('data-bill-no');
            console.log('Editing sale:', billNo);
            openSaleModal(billNo, 'edit');
        });
    });
    
    // Add click listeners to delete buttons
    document.querySelectorAll('.btn-delete').forEach(button => {
        button.addEventListener('click', function() {
            const billNo = this.getAttribute('data-bill-no');
            console.log('Deleting sale:', billNo);
            deleteSale(billNo);
        });
    });
}

// Open sale modal
function openSaleModal(billNo, action) {
    console.log('Opening sale modal:', billNo, action);
    currentModalType = action; // Set current modal type
    const modal = new bootstrap.Modal(document.getElementById('saleModal'));
    
    if (action === 'add') {
        renderAddSaleModal();
        fetchNextBillNumber().then(no => {
            const billField = document.getElementById('sale_bill_no');
            if (billField) billField.value = no;
        });
        saleItemRowCounter = 0;
        const tbody = document.getElementById('saleItemsTableBody');
        if (tbody) tbody.innerHTML = '';
        addSaleItemRow();
        calculateSaleBillTotal();
        modal.show();
    } else {
        fetch(`/api/sales/${action}/${billNo}`)
            .then(response => response.text())
            .then(data => {
                document.querySelector('#saleModal .modal-content').innerHTML = data;
                modal.show();
            })
            .catch(error => {
                console.error('Error loading sale form:', error);
                alert('Error loading sale form. Please try again.');
            });
    }
}

// Open add sale modal
function openAddSaleModal() {
    console.log('Opening add sale modal');
    openSaleModal(null, 'add');
}

// Delete sale
function deleteSale(billNo) {
    if (confirm('Are you sure you want to delete this sale?')) {
        console.log('Deleting sale:', billNo);
        fetch(`/api/sales/delete/${billNo}`, {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Sale deleted successfully!');
                loadSalesTable();
                loadStats();
            } else {
                alert('Error: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error deleting sale:', error);
            alert('Error deleting sale. Please try again.');
        });
    }
}

// Search functionality
function performSearch() {
    const searchTerm = document.getElementById('searchInput').value;
    console.log('Searching for:', searchTerm);
    loadSalesTable();
}

// Debounced search
document.getElementById('searchInput').addEventListener('input', function() {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(performSearch, 500);
});

// Advanced filters
function toggleFilters() {
    const card = document.getElementById('advancedFiltersCard');
    const body = document.getElementById('filterBody');
    const chevron = document.getElementById('filterChevron');
    
    if (card.style.display === 'none') {
        card.style.display = 'block';
        body.style.display = 'block';
        chevron.className = 'fas fa-chevron-up';
    } else {
        card.style.display = 'none';
        body.style.display = 'none';
        chevron.className = 'fas fa-chevron-down';
    }
}

function applyFilters() {
    console.log('Applying filters...');
    loadSalesTable();
}

function clearFilters() {
    document.getElementById('dateFilter').value = '';
    document.getElementById('customerFilter').value = '';
    document.getElementById('amountFilter').value = '';
    document.getElementById('sortByFilter').value = 'date';
    
    console.log('Clearing filters...');
    loadSalesTable();
}

// Export sales
function exportSales() {
    console.log('Exporting sales...');
    const searchTerm = document.getElementById('searchInput').value;
    const dateFilter = document.getElementById('dateFilter') ? document.getElementById('dateFilter').value : '';
    const customerFilter = document.getElementById('customerFilter') ? document.getElementById('customerFilter').value : '';
    const amountFilter = document.getElementById('amountFilter') ? document.getElementById('amountFilter').value : '';
    const sortBy = document.getElementById('sortByFilter') ? document.getElementById('sortByFilter').value : 'date';
    
    const params = new URLSearchParams();
    if (searchTerm) params.append('search', searchTerm);
    if (dateFilter) params.append('date', dateFilter);
    if (customerFilter) params.append('customer', customerFilter);
    if (amountFilter) params.append('amount', amountFilter);
    if (sortBy) params.append('sort', sortBy);
    
    const exportUrl = `/api/sales/export?${params.toString()}`;
    window.open(exportUrl, '_blank');
    console.log('Export initiated');
}

// Global variables for sale form
let saleItemsList = [];
let saleItemRowCounter = 0;
let currentModalType = 'add'; // Track current modal type

// Initialize sale form when modal opens
function initializeSaleForm() {
    console.log('Initializing sale form...');
    
    // Reset form when modal opens
    saleItemRowCounter = 0;
    const tbody = document.getElementById('saleItemsTableBody');
    if (tbody) {
        tbody.innerHTML = '';
    }
    
    // Set today's date
    const today = new Date().toISOString().split('T')[0];
    const dateInput = document.getElementById('sale_bill_date');
    if (dateInput) {
        dateInput.value = today;
    }
    
    // Add first item row immediately
    addSaleItemRow();
}

// Initialize edit sale form
function initializeEditSaleForm() {
    console.log('Initializing edit sale form...');
    console.log('window.editSaleData:', window.editSaleData);
    console.log('window.saleItemsData:', window.saleItemsData);
    
    // Reset form
    saleItemRowCounter = 0;
    const tbody = document.getElementById('editSaleItemsTableBody');
    if (tbody) {
        tbody.innerHTML = '';
    }
    
    // Load existing sale items - FIXED APPROACH
    let saleItems = [];
    
    // Try multiple ways to get the data
    if (window.editSaleData && Array.isArray(window.editSaleData)) {
        saleItems = window.editSaleData;
        console.log('Found sale items in window.editSaleData:', saleItems.length);
    } else if (window.editSaleData && typeof window.editSaleData === 'string') {
        try {
            saleItems = JSON.parse(window.editSaleData);
            console.log('Parsed sale items from string:', saleItems.length);
        } catch (e) {
            console.error('Error parsing editSaleData string:', e);
        }
    } else {
        console.log('No sale items found in window.editSaleData, trying to fetch from server...');
        
        // Get bill number from the form
        const billNoInput = document.getElementById('edit_bill_no');
        if (billNoInput) {
            const billNo = billNoInput.value;
            console.log('Fetching sale items for bill:', billNo);
            
            // Fetch sale items directly from server
            fetch(`/api/sales/items/${billNo}`)
                .then(response => response.json())
                .then(data => {
                    if (data.success && data.items) {
                        saleItems = data.items;
                        console.log('Fetched sale items from server:', saleItems);
                        
                        // Add items to the form
                        if (saleItems.length > 0) {
                            saleItems.forEach((item, index) => {
                                console.log(`Adding item ${index}:`, item);
                                addEditSaleItemRow(item);
                            });
                        } else {
                            console.log('No items found, adding default row');
                            addEditSaleItemRow();
                        }
                        
                        // Calculate totals
                        calculateEditSaleBillTotal();
                    } else {
                        console.log('No items found in server response, adding default row');
                        addEditSaleItemRow();
                        calculateEditSaleBillTotal();
                    }
                })
                .catch(error => {
                    console.error('Error fetching sale items:', error);
                    console.log('Adding default row due to error');
                    addEditSaleItemRow();
                    calculateEditSaleBillTotal();
                });
            return; // Exit early since we're fetching asynchronously
        }
    }
    
    console.log('Loading sale items:', saleItems.length);
    console.log('Sale items data:', saleItems);
    
    if (saleItems.length > 0) {
        saleItems.forEach((item, index) => {
            console.log(`Adding item ${index}:`, item);
            addEditSaleItemRow(item);
        });
    } else {
        console.log('No sale items found, adding default row');
        // Add one default row if no items exist
        addEditSaleItemRow();
    }
    
    // Calculate totals
    calculateEditSaleBillTotal();
}

// Sale form functions - these need to be global
function addSaleItemRow() {
    console.log('Adding sale item row...');
    const tbody = document.getElementById('saleItemsTableBody');
    if (!tbody) {
        console.error('saleItemsTableBody not found');
        return;
    }
    
    const rowId = `sale_row_${saleItemRowCounter}`;
    
    // Get items from global data
    let items = (saleItemsData && saleItemsData.length) ? saleItemsData : (window.saleItemsData || []);
    console.log('Items loaded:', items.length, 'Items data:', items);
    
    // If no items, try to get from server
    if (items.length === 0) {
        console.log('No items found, trying to fetch from server...');
        fetch('/api/items/list')
            .then(response => response.json())
            .then(data => {
                if (data.success && data.items) {
                    window.saleItemsData = data.items;
                    items = data.items;
                    console.log('Items fetched from server:', items);
                    // Re-render the current row with items
                    const currentRow = document.getElementById(rowId);
                    if (currentRow) {
                        const itemSelect = currentRow.querySelector('.sale-item-select');
                        if (itemSelect) {
                            itemSelect.innerHTML = '<option value="">Select Item</option>' + 
                                items.map(item => `<option value="${item.it_cd}" data-rate="${item.rate || 0}" data-gst="${item.gst || 0}">${item.it_cd} - ${item.it_nm}</option>`).join('');
                        }
                    }
                }
            })
            .catch(error => {
                console.error('Error fetching items:', error);
            });
    }
    
    const row = document.createElement('tr');
    row.id = rowId;
    row.innerHTML = `
        <td>
            <select class="form-select bright-input sale-item-select" onchange="onSaleItemSelect(${saleItemRowCounter})" required>
                <option value="">Select Item</option>
                ${items.map(item => `<option value="${item.it_cd}" data-rate="${item.rate || 0}" data-gst="${item.gst || 0}">${item.it_cd} - ${item.it_nm}</option>`).join('')}
            </select>
        </td>
        <td>
            <input type="number" class="form-control bright-input sale-qty-input" step="0.01" min="0" value="1" onchange="calculateSaleRowTotal(${saleItemRowCounter})" required>
        </td>
        <td>
            <input type="number" class="form-control bright-input sale-rate-input" step="0.01" min="0" value="0.00" onchange="calculateSaleRowTotal(${saleItemRowCounter})" required>
        </td>
        <td>
            <input type="number" class="form-control bright-input sale-amount-input" step="0.01" readonly>
        </td>
        <td>
            <input type="number" class="form-control bright-input sale-discount-input" step="0.01" min="0" value="0.00" onchange="calculateSaleRowTotal(${saleItemRowCounter})">
        </td>
        <td>
            <input type="number" class="form-control bright-input sale-net-amount-input" step="0.01" readonly>
        </td>
        <td>
            <button type="button" class="btn btn-sm btn-danger" onclick="removeSaleItemRow(${saleItemRowCounter})">
                <i class="fas fa-trash"></i>
            </button>
        </td>
    `;
    
    tbody.appendChild(row);
    saleItemRowCounter++;
    console.log('Sale item row added, counter:', saleItemRowCounter);
}

function removeSaleItemRow(rowIndex) {
    const row = document.getElementById(`sale_row_${rowIndex}`);
    if (row) {
        row.remove();
        calculateSaleBillTotal();
    }
}

function onSaleItemSelect(rowIndex) {
    const row = document.getElementById(`sale_row_${rowIndex}`);
    if (!row) return;
    
    const itemSelect = row.querySelector('.sale-item-select');
    const rateInput = row.querySelector('.sale-rate-input');
    
    if (itemSelect.value) {
        const selectedOption = itemSelect.options[itemSelect.selectedIndex];
        const rate = selectedOption.getAttribute('data-rate') || 0;
        rateInput.value = rate;
        calculateSaleRowTotal(rowIndex);
    }
}

function calculateSaleRowTotal(rowIndex) {
    const row = document.getElementById(`sale_row_${rowIndex}`);
    if (!row) return;
    
    const qtyInput = row.querySelector('.sale-qty-input');
    const rateInput = row.querySelector('.sale-rate-input');
    const discountInput = row.querySelector('.sale-discount-input');
    const amountInput = row.querySelector('.sale-amount-input');
    const netAmountInput = row.querySelector('.sale-net-amount-input');
    
    const qty = parseFloat(qtyInput.value) || 0;
    const rate = parseFloat(rateInput.value) || 0;
    const discount = parseFloat(discountInput.value) || 0;
    
    const amount = qty * rate;
    const netAmount = amount - discount;
    
    amountInput.value = amount.toFixed(2);
    netAmountInput.value = netAmount.toFixed(2);
    
    calculateSaleBillTotal();
}

function calculateSaleBillTotal() {
    let subTotal = 0;
    let totalDiscount = 0;
    
    const rows = document.querySelectorAll('#saleItemsTableBody tr');
    rows.forEach(row => {
        const amount = parseFloat(row.querySelector('.sale-amount-input').value) || 0;
        const discount = parseFloat(row.querySelector('.sale-discount-input').value) || 0;
        
        subTotal += amount;
        totalDiscount += discount;
    });
    
    const gstAmount = subTotal * 0.18; // 18% GST
    const grandTotal = subTotal - totalDiscount + gstAmount;
    
    const subTotalInput = document.getElementById('sale_sub_total');
    const totalDiscountInput = document.getElementById('sale_total_discount');
    const gstAmountInput = document.getElementById('sale_gst_amount');
    const grandTotalInput = document.getElementById('sale_grand_total');
    
    if (subTotalInput) subTotalInput.value = subTotal.toFixed(2);
    if (totalDiscountInput) totalDiscountInput.value = totalDiscount.toFixed(2);
    if (gstAmountInput) gstAmountInput.value = gstAmount.toFixed(2);
    if (grandTotalInput) grandTotalInput.value = grandTotal.toFixed(2);
}

function saveSale(event) {
    event.preventDefault();
    
    // Validate form
    const billNo = document.getElementById('sale_bill_no').value;
    const billDate = document.getElementById('sale_bill_date').value;
    const partyCd = document.getElementById('sale_party_cd').value;
    
    if (!billNo || !billDate || !partyCd) {
        alert('Please fill in all required fields');
        return;
    }
    
    // Collect items data
    const items = [];
    const rows = document.querySelectorAll('#saleItemsTableBody tr');
    let hasItems = false;
    
    rows.forEach(row => {
        const itemSelect = row.querySelector('.sale-item-select');
        const qtyInput = row.querySelector('.sale-qty-input');
        const rateInput = row.querySelector('.sale-rate-input');
        const discountInput = row.querySelector('.sale-discount-input');
        
        if (itemSelect.value && qtyInput.value && rateInput.value) {
            items.push({
                it_cd: itemSelect.value,
                qty: parseFloat(qtyInput.value),
                rate: parseFloat(rateInput.value),
                discount: parseFloat(discountInput.value) || 0
            });
            hasItems = true;
        }
    });
    
    if (!hasItems) {
        alert('Please add at least one item');
        return;
    }
    
    // Prepare data for submission
    const saleData = {
        bill_no: parseInt(billNo),
        bill_date: billDate,
        party_cd: partyCd,
        items: items,
        sub_total: parseFloat(document.getElementById('sale_sub_total').value),
        total_discount: parseFloat(document.getElementById('sale_total_discount').value),
        gst_amount: parseFloat(document.getElementById('sale_gst_amount').value),
        grand_total: parseFloat(document.getElementById('sale_grand_total').value)
    };
    
    // Submit to API
    fetch('/api/sales/add', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(saleData)
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            alert('Sale bill saved successfully!');
            location.reload();
        } else {
            alert('Error: ' + result.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while saving the sale bill.');
    });
}

// Edit sale form functions
function addEditSaleItemRow(itemData = null) {
    console.log('addEditSaleItemRow called with itemData:', itemData);
    
    const tbody = document.getElementById('editSaleItemsTableBody');
    if (!tbody) {
        console.error('editSaleItemsTableBody not found');
        return;
    }
    
    const rowId = `edit_sale_row_${saleItemRowCounter}`;
    
    // Get items from global data - ENHANCED DATA ACCESS
    let items = [];
    
    // Try multiple ways to get the data
    if (window.saleItemsData && Array.isArray(window.saleItemsData)) {
        items = window.saleItemsData;
        console.log('Using window.saleItemsData (array):', items.length);
    } else if (window.saleItemsData && typeof window.saleItemsData === 'string') {
        try {
            items = JSON.parse(window.saleItemsData);
            console.log('Parsed window.saleItemsData from string:', items.length);
        } catch (e) {
            console.error('Error parsing saleItemsData string:', e);
        }
    } else if (window.saleItemsData && typeof window.saleItemsData === 'object') {
        items = window.saleItemsData;
        console.log('Using window.saleItemsData (object):', items.length);
    } else {
        console.log('No saleItemsData available, trying to fetch from server...');
        
        // Try to fetch items from server as fallback
        fetch('/api/items/list')
            .then(response => response.json())
            .then(data => {
                if (data.success && data.items) {
                    items = data.items;
                    console.log('Fetched items from server:', items.length);
                    // Continue with row creation
                    createEditSaleItemRow(itemData, items, rowId, tbody);
                } else {
                    console.log('No items found in server response');
                    createEditSaleItemRow(itemData, [], rowId, tbody);
                }
            })
            .catch(error => {
                console.error('Error fetching items:', error);
                createEditSaleItemRow(itemData, [], rowId, tbody);
            });
        return; // Exit early since we're fetching asynchronously
    }
    
    console.log('Items loaded for edit:', items.length);
    console.log('Available items:', items);
    
    // Create the row with the items data
    createEditSaleItemRow(itemData, items, rowId, tbody);
}

function createEditSaleItemRow(itemData, items, rowId, tbody) {
    // If itemData is provided, use it to populate the row
    const selectedItem = itemData ? itemData.it_cd : '';
    const qty = itemData ? itemData.qty : 1;
    const rate = itemData ? itemData.rate : 0.00;
    const discount = itemData ? itemData.discount : 0.00;
    const amount = itemData ? itemData.amount : 0.00;
    const netAmount = amount - discount;
    
    console.log('Row data:', {
        selectedItem,
        qty,
        rate,
        discount,
        amount,
        netAmount
    });
    
    // Generate options for the select dropdown
    const options = items.map(item => {
        const selected = item.it_cd === selectedItem ? 'selected' : '';
        return `<option value="${item.it_cd}" data-rate="${item.rate || 0}" data-gst="${item.gst || 0}" ${selected}>${item.it_cd} - ${item.it_nm}</option>`;
    }).join('');
    
    console.log('Generated options:', options);
    
    const row = document.createElement('tr');
    row.id = rowId;
    
    row.innerHTML = `
        <td>
            <select class="form-select bright-input edit-sale-item-select" onchange="onEditSaleItemSelect(${saleItemRowCounter})" required>
                <option value="">Select Item</option>
                ${options}
            </select>
        </td>
        <td>
            <input type="number" class="form-control bright-input edit-sale-qty-input" step="0.01" min="0" value="${qty}" onchange="calculateEditSaleRowTotal(${saleItemRowCounter})" required>
        </td>
        <td>
            <input type="number" class="form-control bright-input edit-sale-rate-input" step="0.01" min="0" value="${rate}" onchange="calculateEditSaleRowTotal(${saleItemRowCounter})" required>
        </td>
        <td>
            <input type="number" class="form-control bright-input edit-sale-amount-input" step="0.01" value="${amount}" readonly>
        </td>
        <td>
            <input type="number" class="form-control bright-input edit-sale-discount-input" step="0.01" min="0" value="${discount}" onchange="calculateEditSaleRowTotal(${saleItemRowCounter})">
        </td>
        <td>
            <input type="number" class="form-control bright-input edit-sale-net-amount-input" step="0.01" value="${netAmount}" readonly>
        </td>
        <td>
            <button type="button" class="btn btn-sm btn-danger" onclick="removeEditSaleItemRow(${saleItemRowCounter})">
                <i class="fas fa-trash"></i>
            </button>
        </td>
    `;
    
    tbody.appendChild(row);
    saleItemRowCounter++;
    
    console.log('Row added successfully with ID:', rowId);
}
    

}

function removeEditSaleItemRow(rowIndex) {
    const row = document.getElementById(`edit_sale_row_${rowIndex}`);
    if (row) {
        row.remove();
        calculateEditSaleBillTotal();
    }
}

function onEditSaleItemSelect(rowIndex) {
    const row = document.getElementById(`edit_sale_row_${rowIndex}`);
    if (!row) return;
    
    const itemSelect = row.querySelector('.edit-sale-item-select');
    const rateInput = row.querySelector('.edit-sale-rate-input');
    
    if (itemSelect.value) {
        const selectedOption = itemSelect.options[itemSelect.selectedIndex];
        const rate = selectedOption.getAttribute('data-rate') || 0;
        rateInput.value = rate;
        calculateEditSaleRowTotal(rowIndex);
    }
}

function calculateEditSaleRowTotal(rowIndex) {
    const row = document.getElementById(`edit_sale_row_${rowIndex}`);
    if (!row) return;
    
    const qtyInput = row.querySelector('.edit-sale-qty-input');
    const rateInput = row.querySelector('.edit-sale-rate-input');
    const discountInput = row.querySelector('.edit-sale-discount-input');
    const amountInput = row.querySelector('.edit-sale-amount-input');
    const netAmountInput = row.querySelector('.edit-sale-net-amount-input');
    
    const qty = parseFloat(qtyInput.value) || 0;
    const rate = parseFloat(rateInput.value) || 0;
    const discount = parseFloat(discountInput.value) || 0;
    
    const amount = qty * rate;
    const netAmount = amount - discount;
    
    amountInput.value = amount.toFixed(2);
    netAmountInput.value = netAmount.toFixed(2);
    
    calculateEditSaleBillTotal();
}

function calculateEditSaleBillTotal() {
    let subTotal = 0;
    let totalDiscount = 0;
    
    const rows = document.querySelectorAll('#editSaleItemsTableBody tr');
    rows.forEach(row => {
        const amount = parseFloat(row.querySelector('.edit-sale-amount-input').value) || 0;
        const discount = parseFloat(row.querySelector('.edit-sale-discount-input').value) || 0;
        
        subTotal += amount;
        totalDiscount += discount;
    });
    
    const gstAmount = subTotal * 0.18; // 18% GST
    const grandTotal = subTotal - totalDiscount + gstAmount;
    
    const subTotalInput = document.getElementById('edit_sub_total');
    const totalDiscountInput = document.getElementById('edit_total_discount');
    const gstAmountInput = document.getElementById('edit_gst_amount');
    const grandTotalInput = document.getElementById('edit_grand_total');
    
    if (subTotalInput) subTotalInput.value = subTotal.toFixed(2);
    if (totalDiscountInput) totalDiscountInput.value = totalDiscount.toFixed(2);
    if (gstAmountInput) gstAmountInput.value = gstAmount.toFixed(2);
    if (grandTotalInput) grandTotalInput.value = grandTotal.toFixed(2);
}

function updateSale(event) {
    event.preventDefault();
    
    console.log('=== UPDATE SALE FUNCTION CALLED ===');
    
    // Validate form
    const billNo = document.getElementById('edit_bill_no').value;
    const billDate = document.getElementById('edit_bill_date').value;
    const partyCd = document.getElementById('edit_party_cd').value;
    
    console.log('Form validation:', { billNo, billDate, partyCd });
    
    if (!billNo || !billDate || !partyCd) {
        alert('Please fill in all required fields');
        return;
    }
    
    // Collect items data
    const items = [];
    const rows = document.querySelectorAll('#editSaleItemsTableBody tr');
    let hasItems = false;
    
    console.log('Found rows:', rows.length);
    
    rows.forEach((row, index) => {
        const itemSelect = row.querySelector('.edit-sale-item-select');
        const qtyInput = row.querySelector('.edit-sale-qty-input');
        const rateInput = row.querySelector('.edit-sale-rate-input');
        const discountInput = row.querySelector('.edit-sale-discount-input');
        
        console.log(`Row ${index}:`, {
            itemSelect: itemSelect ? itemSelect.value : 'not found',
            qtyInput: qtyInput ? qtyInput.value : 'not found',
            rateInput: rateInput ? rateInput.value : 'not found',
            discountInput: discountInput ? discountInput.value : 'not found'
        });
        
        if (itemSelect && itemSelect.value && qtyInput && qtyInput.value && rateInput && rateInput.value) {
            const itemData = {
                it_cd: itemSelect.value,
                qty: parseFloat(qtyInput.value),
                rate: parseFloat(rateInput.value),
                discount: parseFloat(discountInput.value) || 0
            };
            items.push(itemData);
            hasItems = true;
            console.log(`Added item ${index}:`, itemData);
        }
    });
    
    console.log('Collected items:', items);
    console.log('Has items:', hasItems);
    
    if (!hasItems) {
        alert('Please add at least one item');
        return;
    }
    
    // Prepare data for submission
    const saleData = {
        bill_no: parseInt(billNo),
        bill_date: billDate,
        party_cd: partyCd,
        items: items,
        sub_total: parseFloat(document.getElementById('edit_sub_total').value) || 0,
        total_discount: parseFloat(document.getElementById('edit_total_discount').value) || 0,
        gst_amount: parseFloat(document.getElementById('edit_gst_amount').value) || 0,
        grand_total: parseFloat(document.getElementById('edit_grand_total').value) || 0
    };
    
    console.log('Sale data to submit:', saleData);
    
    // Get bill number from the form
    const currentBillNo = billNo;
    
    console.log('Submitting to:', `/api/sales/update/${currentBillNo}`);
    
    // Submit to API
    fetch(`/api/sales/update/${currentBillNo}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(saleData)
    })
    .then(response => {
        console.log('Response status:', response.status);
        return response.json();
    })
    .then(result => {
        console.log('API response:', result);
        if (result.success) {
            alert('Sale bill updated successfully!');
            location.reload();
        } else {
            alert('Error: ' + result.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while updating the sale bill.');
    });
}

// Global variable initialization
window.saleItemsData = window.saleItemsData || [];
window.salePartiesData = window.salePartiesData || [];
window.editSaleData = window.editSaleData || [];

// Modal event handlers
document.addEventListener('DOMContentLoaded', function() {
    const saleModal = document.getElementById('saleModal');
    if (saleModal) {
        saleModal.addEventListener('hidden.bs.modal', function() {
            document.body.style.overflow = 'auto';
            document.body.style.paddingRight = '0';
            console.log('Modal closed, scrollbar restored');
        });
        saleModal.addEventListener('shown.bs.modal', function() {
            document.body.style.overflow = 'auto';
            document.body.style.paddingRight = '0';
            console.log('Modal shown, scrollbar maintained');
            
            // Initialize form based on modal type
            setTimeout(function() {
                if (currentModalType === 'edit') {
                    console.log('Initializing edit form...');
                    console.log('Global data before init:', {
                        saleItemsData: window.saleItemsData,
                        salePartiesData: window.salePartiesData,
                        editSaleData: window.editSaleData
                    });
                    initializeEditSaleForm();
                } else if (currentModalType === 'add') {
                    console.log('Initializing add form...');
                    initializeSaleForm();
                }
                // For 'view' action, no initialization needed as it's read-only
            }, 100);
        });
    }
});
