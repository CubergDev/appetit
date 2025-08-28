class AppetitTester {
    constructor() {
        this.apiBase = 'http://localhost:8000/api/v1';
        this.token = localStorage.getItem('token');
        this.userRole = localStorage.getItem('userRole');
        this.currentSection = 'auth';
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.updateAuthStatus();
        this.loadSection('auth');
    }

    setupEventListeners() {
        // Navigation
        document.querySelectorAll('[data-section]').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const section = e.target.closest('[data-section]').dataset.section;
                this.loadSection(section);
            });
        });

        // Logout
        document.getElementById('logoutBtn').addEventListener('click', () => {
            this.logout();
        });
    }

    async apiCall(endpoint, options = {}) {
        const url = `${this.apiBase}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...(this.token && { 'Authorization': `Bearer ${this.token}` })
            },
            ...options
        };

        if (options.body && typeof options.body === 'object') {
            config.body = JSON.stringify(options.body);
        }

        try {
            const response = await fetch(url, config);
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.detail || `HTTP ${response.status}`);
            }
            
            return data;
        } catch (error) {
            this.showAlert(error.message, 'danger');
            throw error;
        }
    }

    showAlert(message, type = 'info') {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        const content = document.getElementById('content');
        content.insertBefore(alertDiv, content.firstChild);

        // Auto remove after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }

    updateAuthStatus() {
        const authStatus = document.getElementById('authStatus');
        const logoutBtn = document.getElementById('logoutBtn');
        
        if (this.token) {
            authStatus.textContent = `Authenticated (${this.userRole || 'unknown'})`;
            logoutBtn.style.display = 'inline-block';
        } else {
            authStatus.textContent = 'Not authenticated';
            logoutBtn.style.display = 'none';
        }
    }

    logout() {
        localStorage.removeItem('token');
        localStorage.removeItem('userRole');
        this.token = null;
        this.userRole = null;
        this.updateAuthStatus();
        this.loadSection('auth');
        this.showAlert('Logged out successfully', 'success');
    }

    loadSection(section) {
        this.currentSection = section;
        
        // Update active nav item
        document.querySelectorAll('[data-section]').forEach(link => {
            link.classList.remove('active');
        });
        document.querySelector(`[data-section="${section}"]`).classList.add('active');

        // Load content
        const content = document.getElementById('content');
        content.innerHTML = this.getSectionContent(section);
        
        // Setup section-specific event listeners
        this.setupSectionListeners(section);
    }

    getSectionContent(section) {
        switch (section) {
            case 'auth':
                return this.getAuthContent();
            case 'menu':
                return this.getMenuContent();
            case 'orders':
                return this.getOrdersContent();
            case 'cart':
                return this.getCartContent();
            case 'promo':
                return this.getPromoContent();
            case 'integrations':
                return this.getIntegrationsContent();
            case 'analytics':
                return this.getAnalyticsContent();
            case 'banners':
                return this.getBannersContent();
            case 'business-hours':
                return this.getBusinessHoursContent();
            default:
                return '<div class="alert alert-warning">Section not implemented yet</div>';
        }
    }

    getAuthContent() {
        return `
            <div class="row">
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header">
                            <h5><i class="bi bi-person-plus"></i> Register</h5>
                        </div>
                        <div class="card-body">
                            <form id="registerForm">
                                <div class="mb-3">
                                    <label class="form-label">Full Name</label>
                                    <input type="text" class="form-control" name="full_name" required>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Email</label>
                                    <input type="email" class="form-control" name="email">
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Phone</label>
                                    <input type="tel" class="form-control" name="phone">
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Date of Birth</label>
                                    <input type="date" class="form-control" name="dob">
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Password</label>
                                    <input type="password" class="form-control" name="password" required>
                                </div>
                                <button type="submit" class="btn btn-primary">Register</button>
                            </form>
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header">
                            <h5><i class="bi bi-box-arrow-in-right"></i> Login</h5>
                        </div>
                        <div class="card-body">
                            <form id="loginForm">
                                <div class="mb-3">
                                    <label class="form-label">Email or Phone</label>
                                    <input type="text" class="form-control" name="email_or_phone" required>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Password</label>
                                    <input type="password" class="form-control" name="password" required>
                                </div>
                                <button type="submit" class="btn btn-success">Login</button>
                            </form>
                        </div>
                    </div>
                </div>
            </div>

            <div class="row mt-4">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <h5><i class="bi bi-envelope"></i> Email Verification</h5>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <div class="col-md-6">
                                    <form id="emailStartForm">
                                        <div class="mb-3">
                                            <label class="form-label">Email</label>
                                            <input type="email" class="form-control" name="email" required>
                                        </div>
                                        <button type="submit" class="btn btn-outline-primary">Start Email Verification</button>
                                    </form>
                                </div>
                                <div class="col-md-6">
                                    <form id="emailVerifyForm">
                                        <div class="mb-3">
                                            <label class="form-label">Verification Code</label>
                                            <input type="text" class="form-control" name="code" required>
                                        </div>
                                        <div class="mb-3">
                                            <label class="form-label">Token</label>
                                            <input type="text" class="form-control" name="token" required>
                                        </div>
                                        <button type="submit" class="btn btn-success">Verify Email</button>
                                    </form>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="row mt-4">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <h5><i class="bi bi-phone"></i> Phone Verification</h5>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <div class="col-md-6">
                                    <form id="phoneStartForm">
                                        <div class="mb-3">
                                            <label class="form-label">Phone</label>
                                            <input type="tel" class="form-control" name="phone" required>
                                        </div>
                                        <button type="submit" class="btn btn-outline-primary">Start Phone Verification</button>
                                    </form>
                                </div>
                                <div class="col-md-6">
                                    <form id="phoneVerifyForm">
                                        <div class="mb-3">
                                            <label class="form-label">Verification Code</label>
                                            <input type="text" class="form-control" name="code" required>
                                        </div>
                                        <div class="mb-3">
                                            <label class="form-label">Token</label>
                                            <input type="text" class="form-control" name="token" required>
                                        </div>
                                        <button type="submit" class="btn btn-success">Verify Phone</button>
                                    </form>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    getMenuContent() {
        return `
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h2><i class="bi bi-journal-text"></i> Menu Management</h2>
                <div>
                    <button class="btn btn-primary" id="loadMenuBtn">Load Menu</button>
                    <button class="btn btn-success" id="addCategoryBtn">Add Category</button>
                    <button class="btn btn-success" id="addMenuItemBtn">Add Menu Item</button>
                </div>
            </div>

            <div class="row">
                <div class="col-md-4">
                    <div class="card">
                        <div class="card-header">
                            <h5>Categories</h5>
                        </div>
                        <div class="card-body">
                            <div id="categoriesList">
                                <p class="text-muted">Click "Load Menu" to see categories</p>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-md-8">
                    <div class="card">
                        <div class="card-header">
                            <h5>Menu Items</h5>
                        </div>
                        <div class="card-body">
                            <div id="menuItemsList">
                                <p class="text-muted">Click "Load Menu" to see menu items</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Add Category Modal -->
            <div class="modal fade" id="addCategoryModal" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Add Category</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <form id="addCategoryForm">
                                <div class="mb-3">
                                    <label class="form-label">Name</label>
                                    <input type="text" class="form-control" name="name" required>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Sort Order</label>
                                    <input type="number" class="form-control" name="sort" value="0">
                                </div>
                            </form>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                            <button type="button" class="btn btn-primary" id="saveCategoryBtn">Save</button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Add Menu Item Modal -->
            <div class="modal fade" id="addMenuItemModal" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Add Menu Item</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <form id="addMenuItemForm">
                                <div class="mb-3">
                                    <label class="form-label">Category</label>
                                    <select class="form-select" name="category_id" required id="categorySelect">
                                        <option value="">Select Category</option>
                                    </select>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Name</label>
                                    <input type="text" class="form-control" name="name" required>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Description</label>
                                    <textarea class="form-control" name="description" rows="3"></textarea>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Price</label>
                                    <input type="number" class="form-control" name="price" step="0.01" required>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Image URL</label>
                                    <input type="url" class="form-control" name="image_url">
                                </div>
                                <div class="mb-3">
                                    <div class="form-check">
                                        <input type="checkbox" class="form-check-input" name="is_active" checked>
                                        <label class="form-check-label">Is Active</label>
                                    </div>
                                </div>
                            </form>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                            <button type="button" class="btn btn-primary" id="saveMenuItemBtn">Save</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    setupSectionListeners(section) {
        switch (section) {
            case 'auth':
                this.setupAuthListeners();
                break;
            case 'menu':
                this.setupMenuListeners();
                break;
            case 'orders':
                this.setupOrdersListeners();
                break;
            case 'cart':
                this.setupCartListeners();
                break;
            case 'promo':
                this.setupPromoListeners();
                break;
            case 'integrations':
                this.setupIntegrationsListeners();
                break;
            case 'analytics':
                this.setupAnalyticsListeners();
                break;
        }
    }

    setupAuthListeners() {
        // Register form
        document.getElementById('registerForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const data = Object.fromEntries(formData.entries());
            
            try {
                const result = await this.apiCall('/auth/register', {
                    method: 'POST',
                    body: data
                });
                this.showAlert('Registration successful!', 'success');
            } catch (error) {
                // Error already shown in apiCall
            }
        });

        // Login form
        document.getElementById('loginForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const data = Object.fromEntries(formData.entries());
            
            try {
                const result = await this.apiCall('/auth/login', {
                    method: 'POST',
                    body: data
                });
                
                this.token = result.access_token;
                this.userRole = result.user.role;
                localStorage.setItem('token', this.token);
                localStorage.setItem('userRole', this.userRole);
                
                this.updateAuthStatus();
                this.showAlert(`Login successful! Role: ${this.userRole}`, 'success');
            } catch (error) {
                // Error already shown in apiCall
            }
        });

        // Email verification forms
        document.getElementById('emailStartForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const data = Object.fromEntries(formData.entries());
            
            try {
                const result = await this.apiCall('/auth/email/start', {
                    method: 'POST',
                    body: data
                });
                this.showAlert(`Email verification started. Token: ${result.token}`, 'info');
            } catch (error) {
                // Error already shown in apiCall
            }
        });

        document.getElementById('emailVerifyForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const data = Object.fromEntries(formData.entries());
            
            try {
                const result = await this.apiCall('/auth/email/verify', {
                    method: 'POST',
                    body: data
                });
                this.showAlert('Email verified successfully!', 'success');
            } catch (error) {
                // Error already shown in apiCall
            }
        });

        // Phone verification forms
        document.getElementById('phoneStartForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const data = Object.fromEntries(formData.entries());
            
            try {
                const result = await this.apiCall('/auth/phone/start', {
                    method: 'POST',
                    body: data
                });
                this.showAlert(`Phone verification started. Token: ${result.token}`, 'info');
            } catch (error) {
                // Error already shown in apiCall
            }
        });

        document.getElementById('phoneVerifyForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const data = Object.fromEntries(formData.entries());
            
            try {
                const result = await this.apiCall('/auth/phone/verify', {
                    method: 'POST',
                    body: data
                });
                this.showAlert('Phone verified successfully!', 'success');
            } catch (error) {
                // Error already shown in apiCall
            }
        });
    }

    setupMenuListeners() {
        document.getElementById('loadMenuBtn').addEventListener('click', () => {
            this.loadMenu();
        });

        document.getElementById('addCategoryBtn').addEventListener('click', () => {
            new bootstrap.Modal(document.getElementById('addCategoryModal')).show();
        });

        document.getElementById('addMenuItemBtn').addEventListener('click', () => {
            this.loadCategoriesForSelect();
            new bootstrap.Modal(document.getElementById('addMenuItemModal')).show();
        });

        document.getElementById('saveCategoryBtn').addEventListener('click', () => {
            this.saveCategory();
        });

        document.getElementById('saveMenuItemBtn').addEventListener('click', () => {
            this.saveMenuItem();
        });
    }

    setupOrdersListeners() {
        document.getElementById('loadOrdersBtn').addEventListener('click', () => {
            this.loadOrders();
        });

        document.getElementById('createTestOrderBtn').addEventListener('click', () => {
            new bootstrap.Modal(document.getElementById('createOrderModal')).show();
        });

        document.getElementById('saveOrderBtn').addEventListener('click', () => {
            this.createTestOrder();
        });
    }

    setupCartListeners() {
        document.getElementById('loadCartBtn').addEventListener('click', () => {
            this.loadCart();
        });

        document.getElementById('addToCartBtn').addEventListener('click', () => {
            this.showAddToCartModal();
        });

        document.getElementById('clearCartBtn').addEventListener('click', () => {
            this.clearCart();
        });
    }

    setupPromoListeners() {
        document.getElementById('loadPromosBtn').addEventListener('click', () => {
            this.loadPromos();
        });

        document.getElementById('createPromoBtn').addEventListener('click', () => {
            new bootstrap.Modal(document.getElementById('createPromoModal')).show();
        });

        document.getElementById('testPromoBtn').addEventListener('click', () => {
            new bootstrap.Modal(document.getElementById('testPromoModal')).show();
        });

        document.getElementById('savePromoBtn').addEventListener('click', () => {
            this.createPromo();
        });

        document.getElementById('runPromoTestBtn').addEventListener('click', () => {
            this.testPromo();
        });
    }

    setupIntegrationsListeners() {
        document.getElementById('sendSmsBtn').addEventListener('click', () => {
            this.testSms();
        });

        document.getElementById('sendEmailBtn').addEventListener('click', () => {
            this.testEmail();
        });

        document.getElementById('sendPushBtn').addEventListener('click', () => {
            this.testPushNotification();
        });

        document.getElementById('registerDeviceBtn').addEventListener('click', () => {
            this.registerDevice();
        });

        document.getElementById('geocodeBtn').addEventListener('click', () => {
            this.testGeocode();
        });

        document.getElementById('reverseGeocodeBtn').addEventListener('click', () => {
            this.testReverseGeocode();
        });

        document.getElementById('checkIntegrationsBtn').addEventListener('click', () => {
            this.checkIntegrations();
        });
    }

    setupAnalyticsListeners() {
        // Basic analytics loading
        document.getElementById('loadAnalyticsBtn').addEventListener('click', () => {
            this.loadAnalytics();
        });

        document.getElementById('loadAdvancedAnalyticsBtn').addEventListener('click', () => {
            this.loadAdvancedAnalytics();
        });

        document.getElementById('testAnalyticsBtn').addEventListener('click', () => {
            new bootstrap.Modal(document.getElementById('testGA4Modal')).show();
        });

        // Advanced filtering
        document.getElementById('filterAnalyticsBtn').addEventListener('click', () => {
            this.loadAnalyticsWithAdvancedFilters();
        });

        document.getElementById('resetFilterBtn').addEventListener('click', () => {
            this.resetAllFilters();
        });

        document.getElementById('saveFilterBtn').addEventListener('click', () => {
            this.saveFilterPreset();
        });

        document.getElementById('loadFilterBtn').addEventListener('click', () => {
            this.loadFilterPreset();
        });

        // Dish popularity controls
        document.getElementById('loadDishPopularityBtn').addEventListener('click', () => {
            this.loadDishPopularity();
        });

        document.getElementById('dishSortBy').addEventListener('change', () => {
            this.loadDishPopularity();
        });

        document.getElementById('dishSortOrder').addEventListener('change', () => {
            this.loadDishPopularity();
        });

        // Chart period selection
        document.querySelectorAll('input[name="chartPeriod"]').forEach(radio => {
            radio.addEventListener('change', () => {
                this.loadOrdersByPeriod(radio.value);
            });
        });

        // Marketing metrics
        document.getElementById('updateMarketingBtn').addEventListener('click', () => {
            this.showMarketingMetricsModal();
        });

        // Data export
        document.getElementById('exportAnalyticsBtn').addEventListener('click', () => {
            this.exportAnalyticsData();
        });

        // GA4 testing
        document.getElementById('sendGA4EventBtn').addEventListener('click', () => {
            this.sendGA4Event();
        });

        // Sortable table headers
        document.querySelectorAll('.sortable').forEach(header => {
            header.addEventListener('click', () => {
                this.sortTable(header.dataset.sort);
            });
        });
    }

    async loadMenu() {
        try {
            const categories = await this.apiCall('/menu/categories');
            const menuItems = await this.apiCall('/menu/items');

            // Display categories
            const categoriesList = document.getElementById('categoriesList');
            categoriesList.innerHTML = categories.map(cat => `
                <div class="border-bottom py-2">
                    <strong>${cat.name}</strong> (ID: ${cat.id}, Sort: ${cat.sort})
                </div>
            `).join('');

            // Display menu items
            const menuItemsList = document.getElementById('menuItemsList');
            menuItemsList.innerHTML = menuItems.map(item => `
                <div class="border p-3 mb-3 rounded">
                    <div class="d-flex justify-content-between align-items-start">
                        <div>
                            <h6>${item.name}</h6>
                            <p class="text-muted mb-1">${item.description || 'No description'}</p>
                            <p class="mb-1"><strong>Price: $${item.price}</strong></p>
                            <small class="text-muted">Category ID: ${item.category_id}, Active: ${item.is_active}</small>
                        </div>
                        ${item.image_url ? `<img src="${item.image_url}" class="img-thumbnail" style="width: 80px; height: 80px; object-fit: cover;">` : ''}
                    </div>
                </div>
            `).join('');

        } catch (error) {
            // Error already shown in apiCall
        }
    }

    async loadCategoriesForSelect() {
        try {
            const categories = await this.apiCall('/menu/categories');
            const select = document.getElementById('categorySelect');
            select.innerHTML = '<option value="">Select Category</option>' + 
                categories.map(cat => `<option value="${cat.id}">${cat.name}</option>`).join('');
        } catch (error) {
            // Error already shown in apiCall
        }
    }

    async saveCategory() {
        const form = document.getElementById('addCategoryForm');
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());
        data.sort = parseInt(data.sort);

        try {
            await this.apiCall('/admin/menu/categories', {
                method: 'POST',
                body: data
            });
            
            this.showAlert('Category created successfully!', 'success');
            bootstrap.Modal.getInstance(document.getElementById('addCategoryModal')).hide();
            this.loadMenu();
        } catch (error) {
            // Error already shown in apiCall
        }
    }

    async saveMenuItem() {
        const form = document.getElementById('addMenuItemForm');
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());
        data.category_id = parseInt(data.category_id);
        data.price = parseFloat(data.price);
        data.is_active = formData.has('is_active');

        try {
            await this.apiCall('/admin/menu/items', {
                method: 'POST',
                body: data
            });
            
            this.showAlert('Menu item created successfully!', 'success');
            bootstrap.Modal.getInstance(document.getElementById('addMenuItemModal')).hide();
            this.loadMenu();
        } catch (error) {
            // Error already shown in apiCall
        }
    }

    async loadOrders() {
        try {
            const orders = await this.apiCall('/orders');
            
            const ordersList = document.getElementById('ordersList');
            if (orders.length === 0) {
                ordersList.innerHTML = '<p class="text-muted">No orders found</p>';
                return;
            }

            ordersList.innerHTML = orders.map(order => `
                <div class="border p-3 mb-3 rounded">
                    <div class="d-flex justify-content-between align-items-start">
                        <div>
                            <h6>Order #${order.number}</h6>
                            <p class="mb-1"><strong>Status:</strong> <span class="badge bg-${this.getStatusColor(order.status)}">${order.status}</span></p>
                            <p class="mb-1"><strong>Total:</strong> $${order.total}</p>
                            <p class="mb-1"><strong>Fulfillment:</strong> ${order.fulfillment}</p>
                            <p class="mb-1"><strong>Payment:</strong> ${order.payment_method} ${order.paid ? '(Paid)' : '(Unpaid)'}</p>
                            ${order.address_text ? `<p class="mb-1"><strong>Address:</strong> ${order.address_text}</p>` : ''}
                            <small class="text-muted">Created: ${new Date(order.created_at).toLocaleString()}</small>
                        </div>
                        <div>
                            <button class="btn btn-sm btn-outline-primary me-2" onclick="app.viewOrderDetails(${order.id})">
                                Details
                            </button>
                            <div class="btn-group" role="group">
                                <button class="btn btn-sm btn-success" onclick="app.updateOrderStatus(${order.id}, 'COOKING')" 
                                    ${order.status === 'COOKING' ? 'disabled' : ''}>Cooking</button>
                                <button class="btn btn-sm btn-warning" onclick="app.updateOrderStatus(${order.id}, 'ON_WAY')" 
                                    ${order.status === 'ON_WAY' ? 'disabled' : ''}>On Way</button>
                                <button class="btn btn-sm btn-info" onclick="app.updateOrderStatus(${order.id}, 'DELIVERED')" 
                                    ${order.status === 'DELIVERED' ? 'disabled' : ''}>Delivered</button>
                                <button class="btn btn-sm btn-danger" onclick="app.updateOrderStatus(${order.id}, 'CANCELLED')" 
                                    ${order.status === 'CANCELLED' ? 'disabled' : ''}>Cancel</button>
                            </div>
                        </div>
                    </div>
                </div>
            `).join('');

        } catch (error) {
            // Error already shown in apiCall
        }
    }

    async viewOrderDetails(orderId) {
        try {
            const order = await this.apiCall(`/orders/${orderId}`);
            
            const content = `
                <div class="row">
                    <div class="col-md-6">
                        <h6>Order Information</h6>
                        <table class="table table-sm">
                            <tr><th>Number:</th><td>#${order.number}</td></tr>
                            <tr><th>Status:</th><td><span class="badge bg-${this.getStatusColor(order.status)}">${order.status}</span></td></tr>
                            <tr><th>Fulfillment:</th><td>${order.fulfillment}</td></tr>
                            <tr><th>Payment:</th><td>${order.payment_method} ${order.paid ? '(Paid)' : '(Unpaid)'}</td></tr>
                            <tr><th>Subtotal:</th><td>$${order.subtotal}</td></tr>
                            <tr><th>Discount:</th><td>$${order.discount}</td></tr>
                            <tr><th>Total:</th><td><strong>$${order.total}</strong></td></tr>
                            ${order.promocode_code ? `<tr><th>Promo Code:</th><td>${order.promocode_code}</td></tr>` : ''}
                            ${order.address_text ? `<tr><th>Address:</th><td>${order.address_text}</td></tr>` : ''}
                            <tr><th>Created:</th><td>${new Date(order.created_at).toLocaleString()}</td></tr>
                        </table>
                    </div>
                    <div class="col-md-6">
                        <h6>Order Items</h6>
                        <div class="list-group list-group-flush">
                            ${order.items.map(item => `
                                <div class="list-group-item d-flex justify-content-between align-items-center">
                                    <div>
                                        <strong>${item.name_snapshot}</strong>
                                        <br><small class="text-muted">Qty: ${item.qty}</small>
                                    </div>
                                    <span class="badge bg-primary rounded-pill">$${item.price_at_moment}</span>
                                </div>
                            `).join('')}
                        </div>
                        ${order.utm_source || order.utm_medium || order.utm_campaign ? `
                            <h6 class="mt-3">Analytics</h6>
                            <table class="table table-sm">
                                ${order.utm_source ? `<tr><th>UTM Source:</th><td>${order.utm_source}</td></tr>` : ''}
                                ${order.utm_medium ? `<tr><th>UTM Medium:</th><td>${order.utm_medium}</td></tr>` : ''}
                                ${order.utm_campaign ? `<tr><th>UTM Campaign:</th><td>${order.utm_campaign}</td></tr>` : ''}
                                ${order.ga_client_id ? `<tr><th>GA Client ID:</th><td>${order.ga_client_id}</td></tr>` : ''}
                            </table>
                        ` : ''}
                    </div>
                </div>
            `;
            
            document.getElementById('orderDetailsContent').innerHTML = content;
            new bootstrap.Modal(document.getElementById('orderDetailsModal')).show();

        } catch (error) {
            // Error already shown in apiCall
        }
    }

    async updateOrderStatus(orderId, status) {
        try {
            await this.apiCall(`/admin/orders/${orderId}/status`, {
                method: 'PATCH',
                body: { status }
            });
            
            this.showAlert(`Order status updated to ${status}`, 'success');
            this.loadOrders();

        } catch (error) {
            // Error already shown in apiCall
        }
    }

    async createTestOrder() {
        const form = document.getElementById('createOrderForm');
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());

        // First, we need to add items to cart
        try {
            // Get first menu item for testing
            const menuItems = await this.apiCall('/menu/items');
            if (menuItems.length === 0) {
                this.showAlert('No menu items found. Create a menu item first.', 'warning');
                return;
            }

            // Add item to cart
            await this.apiCall('/cart/add', {
                method: 'POST',
                body: {
                    item_id: menuItems[0].id,
                    qty: 1
                }
            });

            // Create order from cart
            const orderData = {
                fulfillment: data.fulfillment,
                payment_method: data.payment_method,
                ...(data.address_text && { address_text: data.address_text }),
                ...(data.promo_code && { promo_code: data.promo_code }),
                ...(data.utm_source && { utm_source: data.utm_source })
            };

            const order = await this.apiCall('/orders', {
                method: 'POST',
                body: orderData
            });
            
            this.showAlert(`Test order created: #${order.number}`, 'success');
            bootstrap.Modal.getInstance(document.getElementById('createOrderModal')).hide();
            this.loadOrders();

        } catch (error) {
            // Error already shown in apiCall
        }
    }

    getStatusColor(status) {
        const colors = {
            'NEW': 'secondary',
            'COOKING': 'warning',
            'ON_WAY': 'info',
            'DELIVERED': 'success',
            'CANCELLED': 'danger'
        };
        return colors[status] || 'secondary';
    }

    async loadCart() {
        try {
            const cart = await this.apiCall('/cart');
            
            const cartItemsList = document.getElementById('cartItemsList');
            const cartSummary = document.getElementById('cartSummary');
            
            if (!cart || !cart.items || cart.items.length === 0) {
                cartItemsList.innerHTML = '<p class="text-muted">Cart is empty</p>';
                cartSummary.innerHTML = '<p class="text-muted">Cart is empty</p>';
                return;
            }

            // Display cart items
            cartItemsList.innerHTML = cart.items.map(item => `
                <div class="border p-3 mb-2 rounded">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <h6>${item.menu_item.name}</h6>
                            <p class="mb-1">Price: $${item.menu_item.price}</p>
                            <div class="d-flex align-items-center">
                                <button class="btn btn-sm btn-outline-secondary" onclick="app.updateCartItemQty(${item.id}, ${item.qty - 1})">-</button>
                                <span class="mx-3">Qty: ${item.qty}</span>
                                <button class="btn btn-sm btn-outline-secondary" onclick="app.updateCartItemQty(${item.id}, ${item.qty + 1})">+</button>
                            </div>
                        </div>
                        <div>
                            <p class="mb-2"><strong>$${(item.menu_item.price * item.qty).toFixed(2)}</strong></p>
                            <button class="btn btn-sm btn-danger" onclick="app.removeFromCart(${item.id})">Remove</button>
                        </div>
                    </div>
                </div>
            `).join('');

            // Calculate and display summary
            const subtotal = cart.items.reduce((sum, item) => sum + (item.menu_item.price * item.qty), 0);
            cartSummary.innerHTML = `
                <p><strong>Items: ${cart.items.length}</strong></p>
                <p><strong>Subtotal: $${subtotal.toFixed(2)}</strong></p>
                <button class="btn btn-success w-100" onclick="app.proceedToCheckout()">Proceed to Checkout</button>
            `;

        } catch (error) {
            // Error already shown in apiCall
        }
    }

    async showAddToCartModal() {
        try {
            const menuItems = await this.apiCall('/menu/items');
            
            if (menuItems.length === 0) {
                this.showAlert('No menu items found. Add some menu items first.', 'warning');
                return;
            }

            // Create a simple modal for adding items
            const modalHtml = `
                <div class="modal fade" id="addToCartModal" tabindex="-1">
                    <div class="modal-dialog">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title">Add to Cart</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body">
                                <div class="mb-3">
                                    <label class="form-label">Menu Item</label>
                                    <select class="form-select" id="selectMenuItem">
                                        ${menuItems.map(item => `<option value="${item.id}">${item.name} - $${item.price}</option>`).join('')}
                                    </select>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Quantity</label>
                                    <input type="number" class="form-control" id="itemQuantity" value="1" min="1">
                                </div>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                                <button type="button" class="btn btn-primary" onclick="app.addItemToCart()">Add to Cart</button>
                            </div>
                        </div>
                    </div>
                </div>
            `;

            // Remove existing modal if any
            const existingModal = document.getElementById('addToCartModal');
            if (existingModal) {
                existingModal.remove();
            }

            // Add modal to page
            document.body.insertAdjacentHTML('beforeend', modalHtml);
            new bootstrap.Modal(document.getElementById('addToCartModal')).show();

        } catch (error) {
            // Error already shown in apiCall
        }
    }

    async addItemToCart() {
        const itemId = parseInt(document.getElementById('selectMenuItem').value);
        const qty = parseInt(document.getElementById('itemQuantity').value);

        try {
            await this.apiCall('/cart/add', {
                method: 'POST',
                body: { item_id: itemId, qty }
            });

            this.showAlert('Item added to cart!', 'success');
            bootstrap.Modal.getInstance(document.getElementById('addToCartModal')).hide();
            this.loadCart();

        } catch (error) {
            // Error already shown in apiCall
        }
    }

    async updateCartItemQty(cartItemId, newQty) {
        if (newQty <= 0) {
            this.removeFromCart(cartItemId);
            return;
        }

        try {
            await this.apiCall(`/cart/items/${cartItemId}`, {
                method: 'PATCH',
                body: { qty: newQty }
            });

            this.loadCart();

        } catch (error) {
            // Error already shown in apiCall
        }
    }

    async removeFromCart(cartItemId) {
        try {
            await this.apiCall(`/cart/items/${cartItemId}`, {
                method: 'DELETE'
            });

            this.showAlert('Item removed from cart', 'success');
            this.loadCart();

        } catch (error) {
            // Error already shown in apiCall
        }
    }

    async clearCart() {
        try {
            await this.apiCall('/cart/clear', {
                method: 'DELETE'
            });

            this.showAlert('Cart cleared', 'success');
            this.loadCart();

        } catch (error) {
            // Error already shown in apiCall
        }
    }

    async proceedToCheckout() {
        this.showAlert('Checkout functionality - use Orders section to create orders from cart', 'info');
    }

    async loadPromos() {
        try {
            const promos = await this.apiCall('/admin/promo/codes');
            
            const promosList = document.getElementById('promosList');
            if (promos.length === 0) {
                promosList.innerHTML = '<p class="text-muted">No promocodes found</p>';
                return;
            }

            promosList.innerHTML = promos.map(promo => `
                <div class="border p-3 mb-3 rounded">
                    <div class="d-flex justify-content-between align-items-start">
                        <div>
                            <h6>${promo.code}</h6>
                            <p class="mb-1"><strong>Type:</strong> ${promo.kind} | <strong>Value:</strong> ${promo.value}${promo.kind === 'percent' ? '%' : '$'}</p>
                            <p class="mb-1"><strong>Status:</strong> <span class="badge bg-${promo.active ? 'success' : 'secondary'}">${promo.active ? 'Active' : 'Inactive'}</span></p>
                            ${promo.valid_from ? `<p class="mb-1"><strong>Valid From:</strong> ${new Date(promo.valid_from).toLocaleString()}</p>` : ''}
                            ${promo.valid_to ? `<p class="mb-1"><strong>Valid To:</strong> ${new Date(promo.valid_to).toLocaleString()}</p>` : ''}
                            ${promo.max_redemptions ? `<p class="mb-1"><strong>Max Redemptions:</strong> ${promo.max_redemptions}</p>` : ''}
                            ${promo.per_user_limit ? `<p class="mb-1"><strong>Per User Limit:</strong> ${promo.per_user_limit}</p>` : ''}
                            ${promo.min_subtotal ? `<p class="mb-1"><strong>Min Subtotal:</strong> $${promo.min_subtotal}</p>` : ''}
                            <small class="text-muted">Created: ${new Date(promo.created_at).toLocaleString()}</small>
                        </div>
                        <div>
                            <button class="btn btn-sm btn-outline-primary me-2" onclick="app.testSpecificPromo('${promo.code}')">Test</button>
                            <button class="btn btn-sm btn-${promo.active ? 'warning' : 'success'}" onclick="app.togglePromo('${promo.code}', ${!promo.active})">
                                ${promo.active ? 'Deactivate' : 'Activate'}
                            </button>
                        </div>
                    </div>
                </div>
            `).join('');

        } catch (error) {
            // Error already shown in apiCall
        }
    }

    async createPromo() {
        const form = document.getElementById('createPromoForm');
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());
        
        // Convert values to proper types
        data.value = parseFloat(data.value);
        data.active = formData.has('active');
        if (data.max_redemptions) data.max_redemptions = parseInt(data.max_redemptions);
        if (data.per_user_limit) data.per_user_limit = parseInt(data.per_user_limit);
        if (data.min_subtotal) data.min_subtotal = parseFloat(data.min_subtotal);

        // Remove empty fields
        Object.keys(data).forEach(key => {
            if (data[key] === '' || data[key] === null || data[key] === undefined) {
                delete data[key];
            }
        });

        try {
            await this.apiCall('/admin/promo/codes', {
                method: 'POST',
                body: data
            });
            
            this.showAlert('Promocode created successfully!', 'success');
            bootstrap.Modal.getInstance(document.getElementById('createPromoModal')).hide();
            this.loadPromos();

        } catch (error) {
            // Error already shown in apiCall
        }
    }

    async testPromo() {
        const form = document.getElementById('testPromoForm');
        const formData = new FormData(form);
        const code = formData.get('code');
        const subtotal = parseFloat(formData.get('subtotal'));

        try {
            const result = await this.apiCall('/promo/validate', {
                method: 'POST',
                body: { code, subtotal }
            });

            const resultDiv = document.getElementById('promoTestResult');
            resultDiv.innerHTML = `
                <div class="alert alert-success">
                    <h6>✓ Promocode Valid!</h6>
                    <p><strong>Code:</strong> ${result.code}</p>
                    <p><strong>Discount:</strong> $${result.discount.toFixed(2)}</p>
                    <p><strong>New Total:</strong> $${(subtotal - result.discount).toFixed(2)}</p>
                </div>
            `;

        } catch (error) {
            const resultDiv = document.getElementById('promoTestResult');
            resultDiv.innerHTML = `
                <div class="alert alert-danger">
                    <h6>✗ Promocode Invalid</h6>
                    <p>${error.message}</p>
                </div>
            `;
        }
    }

    async testSpecificPromo(code) {
        // Fill the test modal with the specific code
        document.querySelector('#testPromoModal input[name="code"]').value = code;
        new bootstrap.Modal(document.getElementById('testPromoModal')).show();
    }

    async togglePromo(code, newActiveState) {
        try {
            await this.apiCall(`/admin/promo/codes/${code}`, {
                method: 'PATCH',
                body: { active: newActiveState }
            });
            
            this.showAlert(`Promocode ${newActiveState ? 'activated' : 'deactivated'}`, 'success');
            this.loadPromos();

        } catch (error) {
            // Error already shown in apiCall
        }
    }

    async testSms() {
        const form = document.getElementById('smsTestForm');
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());

        try {
            await this.apiCall('/admin/integrations/sms/test', {
                method: 'POST',
                body: data
            });
            
            this.showAlert('SMS sent successfully!', 'success');

        } catch (error) {
            // Error already shown in apiCall
        }
    }

    async testEmail() {
        const form = document.getElementById('emailTestForm');
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());

        try {
            await this.apiCall('/admin/integrations/email/test', {
                method: 'POST',
                body: data
            });
            
            this.showAlert('Email sent successfully!', 'success');

        } catch (error) {
            // Error already shown in apiCall
        }
    }

    async testPushNotification() {
        const form = document.getElementById('pushTestForm');
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());

        try {
            await this.apiCall('/admin/push/send', {
                method: 'POST',
                body: {
                    title: data.title,
                    body: data.body,
                    target: data.target
                }
            });
            
            this.showAlert('Push notification sent successfully!', 'success');

        } catch (error) {
            // Error already shown in apiCall
        }
    }

    async registerDevice() {
        const form = document.getElementById('deviceRegisterForm');
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());

        if (!data.fcm_token.trim()) {
            this.showAlert('FCM token is required', 'warning');
            return;
        }

        try {
            await this.apiCall('/devices/register', {
                method: 'POST',
                body: {
                    fcm_token: data.fcm_token,
                    platform: data.platform
                }
            });
            
            this.showAlert('Device registered successfully!', 'success');
            form.reset();

        } catch (error) {
            // Error already shown in apiCall
        }
    }

    async testGeocode() {
        const form = document.getElementById('geocodeTestForm');
        const formData = new FormData(form);
        const address = formData.get('address');

        try {
            const result = await this.apiCall('/maps/geocode', {
                method: 'POST',
                body: { address }
            });
            
            const resultDiv = document.getElementById('geocodeResult');
            resultDiv.innerHTML = `
                <div class="alert alert-success">
                    <h6>✓ Geocoding Result</h6>
                    <p><strong>Address:</strong> ${result.formatted_address}</p>
                    <p><strong>Coordinates:</strong> ${result.lat}, ${result.lng}</p>
                    ${result.place_id ? `<p><strong>Place ID:</strong> ${result.place_id}</p>` : ''}
                </div>
            `;

        } catch (error) {
            const resultDiv = document.getElementById('geocodeResult');
            resultDiv.innerHTML = `
                <div class="alert alert-danger">
                    <h6>✗ Geocoding Failed</h6>
                    <p>${error.message}</p>
                </div>
            `;
        }
    }

    async testReverseGeocode() {
        const form = document.getElementById('reverseGeocodeForm');
        const formData = new FormData(form);
        const lat = parseFloat(formData.get('lat'));
        const lng = parseFloat(formData.get('lng'));

        try {
            const result = await this.apiCall('/maps/reverse-geocode', {
                method: 'POST',
                body: { lat, lng }
            });
            
            const resultDiv = document.getElementById('reverseGeocodeResult');
            resultDiv.innerHTML = `
                <div class="alert alert-success">
                    <h6>✓ Reverse Geocoding Result</h6>
                    <p><strong>Address:</strong> ${result.formatted_address}</p>
                    <p><strong>Coordinates:</strong> ${lat}, ${lng}</p>
                    ${result.place_id ? `<p><strong>Place ID:</strong> ${result.place_id}</p>` : ''}
                </div>
            `;

        } catch (error) {
            const resultDiv = document.getElementById('reverseGeocodeResult');
            resultDiv.innerHTML = `
                <div class="alert alert-danger">
                    <h6>✗ Reverse Geocoding Failed</h6>
                    <p>${error.message}</p>
                </div>
            `;
        }
    }

    async loadAnalytics(useFilter = false) {
        try {
            let endpoint = '/admin/analytics';
            const params = new URLSearchParams();
            
            if (useFilter) {
                const fromDate = document.getElementById('fromDate').value;
                const toDate = document.getElementById('toDate').value;
                if (fromDate) params.append('from', fromDate);
                if (toDate) params.append('to', toDate);
            }
            
            if (params.toString()) {
                endpoint += '?' + params.toString();
            }
            
            const analytics = await this.apiCall(endpoint);
            
            // Update summary cards
            document.getElementById('totalOrders').textContent = analytics.total_orders || '0';
            document.getElementById('totalRevenue').textContent = '$' + (analytics.total_revenue || '0.00');
            document.getElementById('avgOrder').textContent = '$' + (analytics.average_order || '0.00');
            document.getElementById('activeUsers').textContent = analytics.active_users || '0';
            
            // Update UTM sources
            const utmDiv = document.getElementById('utmSources');
            if (analytics.utm_sources && analytics.utm_sources.length > 0) {
                utmDiv.innerHTML = analytics.utm_sources.map(source => `
                    <div class="d-flex justify-content-between border-bottom py-2">
                        <span>${source.source || 'Direct'}</span>
                        <span class="badge bg-primary">${source.count}</span>
                    </div>
                `).join('');
            } else {
                utmDiv.innerHTML = '<p class="text-muted">No UTM data found</p>';
            }
            
            // Update order status
            const statusDiv = document.getElementById('orderStatus');
            if (analytics.order_status && analytics.order_status.length > 0) {
                statusDiv.innerHTML = analytics.order_status.map(status => `
                    <div class="d-flex justify-content-between border-bottom py-2">
                        <span>${status.status}</span>
                        <span class="badge bg-${this.getStatusColor(status.status)}">${status.count}</span>
                    </div>
                `).join('');
            } else {
                statusDiv.innerHTML = '<p class="text-muted">No order status data found</p>';
            }
            
            // Update recent orders table
            const tableBody = document.getElementById('recentOrdersTable');
            if (analytics.recent_orders && analytics.recent_orders.length > 0) {
                tableBody.innerHTML = analytics.recent_orders.map(order => `
                    <tr>
                        <td>#${order.number}</td>
                        <td>${new Date(order.created_at).toLocaleDateString()}</td>
                        <td>$${order.total}</td>
                        <td>${order.utm_source || '-'}</td>
                        <td>${order.utm_medium || '-'}</td>
                        <td>${order.utm_campaign || '-'}</td>
                        <td>${order.ga_client_id || '-'}</td>
                    </tr>
                `).join('');
            } else {
                tableBody.innerHTML = '<tr><td colspan="7" class="text-center text-muted">No recent orders found</td></tr>';
            }

        } catch (error) {
            // Error already shown in apiCall
        }
    }

    async sendGA4Event() {
        const form = document.getElementById('ga4TestForm');
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());

        try {
            let parameters = {};
            if (data.parameters) {
                parameters = JSON.parse(data.parameters);
            }

            await this.apiCall('/admin/analytics/ga4/test', {
                method: 'POST',
                body: {
                    event_name: data.event_name,
                    client_id: data.client_id,
                    parameters
                }
            });
            
            this.showAlert('GA4 event sent successfully!', 'success');
            bootstrap.Modal.getInstance(document.getElementById('testGA4Modal')).hide();

        } catch (error) {
            // Error already shown in apiCall
        }
    }

    // Advanced Analytics Methods
    async loadAdvancedAnalytics() {
        await Promise.all([
            this.loadAnalytics(true),
            this.loadDishPopularity(),
            this.loadOrdersByPeriod('day'),
            this.loadRepeatCustomers(),
            this.loadMarketingMetrics()
        ]);
        this.showAlert('Advanced analytics loaded successfully!', 'success');
    }

    async loadDishPopularity() {
        try {
            const sortBy = document.getElementById('dishSortBy')?.value || 'qty';
            const sortOrder = document.getElementById('dishSortOrder')?.value || 'desc';
            const fromDate = document.getElementById('fromDate')?.value;
            const toDate = document.getElementById('toDate')?.value;
            const fulfillmentType = document.getElementById('fulfillmentFilter')?.value;

            let endpoint = `/admin/analytics/dish-popularity?sort_by=${sortBy}&order=${sortOrder}&limit=50`;
            if (fromDate) endpoint += `&from=${fromDate}`;
            if (toDate) endpoint += `&to=${toDate}`;
            if (fulfillmentType) endpoint += `&type=${fulfillmentType}`;

            const dishes = await this.apiCall(endpoint);
            
            const tableBody = document.getElementById('dishPopularityTable');
            if (dishes && dishes.length > 0) {
                tableBody.innerHTML = dishes.map(dish => `
                    <tr>
                        <td><strong>${dish.name}</strong></td>
                        <td class="text-end">${dish.total_qty || 0}</td>
                        <td class="text-end">$${(dish.total_revenue || 0).toFixed(2)}</td>
                        <td class="text-end">$${(dish.avg_price || 0).toFixed(2)}</td>
                        <td class="text-center">
                            <button class="btn btn-sm btn-outline-info" onclick="app.viewDishDetails(${dish.id})">
                                <i class="bi bi-eye"></i>
                            </button>
                        </td>
                    </tr>
                `).join('');
            } else {
                tableBody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">No dish data found</td></tr>';
            }

        } catch (error) {
            document.getElementById('dishPopularityTable').innerHTML = 
                '<tr><td colspan="5" class="text-center text-danger">Error loading dish popularity data</td></tr>';
        }
    }

    async loadOrdersByPeriod(period = 'day') {
        try {
            const fromDate = document.getElementById('fromDate')?.value;
            const toDate = document.getElementById('toDate')?.value;

            let endpoint = `/admin/analytics/orders-by-period?period=${period}`;
            if (fromDate) endpoint += `&from=${fromDate}`;
            if (toDate) endpoint += `&to=${toDate}`;

            const data = await this.apiCall(endpoint);
            
            const chartDiv = document.getElementById('ordersChart');
            if (data && data.length > 0) {
                // Simple chart representation using HTML/CSS bars
                const maxOrders = Math.max(...data.map(d => d.orders));
                chartDiv.innerHTML = `
                    <div class="chart-container">
                        ${data.map(item => `
                            <div class="chart-bar-container d-flex align-items-end mb-2">
                                <div class="chart-label me-2" style="width: 100px; font-size: 0.8em;">
                                    ${item.period}
                                </div>
                                <div class="chart-bar bg-primary" style="height: 20px; width: ${(item.orders / maxOrders) * 200}px; min-width: 2px;">
                                </div>
                                <div class="chart-value ms-2 small">
                                    ${item.orders} orders ($${item.revenue || 0})
                                </div>
                            </div>
                        `).join('')}
                    </div>
                `;
            } else {
                chartDiv.innerHTML = '<p class="text-muted">No order data found for selected period</p>';
            }

        } catch (error) {
            document.getElementById('ordersChart').innerHTML = 
                '<p class="text-danger">Error loading orders by period data</p>';
        }
    }

    async loadRepeatCustomers() {
        try {
            const fromDate = document.getElementById('fromDate')?.value;
            const toDate = document.getElementById('toDate')?.value;

            let endpoint = '/admin/analytics/repeat-customers';
            const params = new URLSearchParams();
            if (fromDate) params.append('from', fromDate);
            if (toDate) params.append('to', toDate);
            if (params.toString()) endpoint += '?' + params.toString();

            const data = await this.apiCall(endpoint);
            
            document.getElementById('repeatCustomers').textContent = data.repeat_customers || '0';
            document.getElementById('repeatRate').textContent = `${(data.repeat_rate || 0).toFixed(1)}% repeat rate`;

        } catch (error) {
            document.getElementById('repeatCustomers').textContent = 'Error';
            document.getElementById('repeatRate').textContent = 'Failed to load';
        }
    }

    async loadMarketingMetrics() {
        try {
            const fromDate = document.getElementById('fromDate')?.value;
            const toDate = document.getElementById('toDate')?.value;

            let endpoint = '/admin/analytics/marketing-metrics';
            const params = new URLSearchParams();
            if (fromDate) params.append('from', fromDate);
            if (toDate) params.append('to', toDate);
            if (params.toString()) endpoint += '?' + params.toString();

            const data = await this.apiCall(endpoint);
            
            const metricsDiv = document.getElementById('marketingMetrics');
            metricsDiv.innerHTML = `
                <div class="row g-2">
                    <div class="col-4 text-center">
                        <div class="border rounded p-2">
                            <small class="text-muted">CAC</small><br>
                            <strong>$${(data.cac || 0).toFixed(2)}</strong>
                        </div>
                    </div>
                    <div class="col-4 text-center">
                        <div class="border rounded p-2">
                            <small class="text-muted">LTV</small><br>
                            <strong>$${(data.ltv || 0).toFixed(2)}</strong>
                        </div>
                    </div>
                    <div class="col-4 text-center">
                        <div class="border rounded p-2">
                            <small class="text-muted">ROAS</small><br>
                            <strong>${(data.roas || 0).toFixed(1)}x</strong>
                        </div>
                    </div>
                </div>
                <div class="mt-3">
                    <small class="text-muted">
                        Conversion Rate: ${(data.conversion_rate || 0).toFixed(1)}% | 
                        Total Spend: $${(data.total_spend || 0).toFixed(2)} | 
                        Total Installs: ${data.total_installs || 0}
                    </small>
                </div>
            `;

        } catch (error) {
            document.getElementById('marketingMetrics').innerHTML = 
                '<p class="text-danger">Error loading marketing metrics</p>';
        }
    }

    async loadAnalyticsWithAdvancedFilters() {
        const fromDate = document.getElementById('fromDate')?.value;
        const toDate = document.getElementById('toDate')?.value;
        const period = document.getElementById('periodSelect')?.value || 'day';
        const fulfillment = document.getElementById('fulfillmentFilter')?.value;

        // Apply filters to all analytics components
        await Promise.all([
            this.loadAnalytics(true),
            this.loadDishPopularity(),
            this.loadOrdersByPeriod(period),
            this.loadRepeatCustomers(),
            this.loadMarketingMetrics()
        ]);
        
        this.showAlert('Filters applied successfully!', 'success');
    }

    resetAllFilters() {
        document.getElementById('fromDate').value = '';
        document.getElementById('toDate').value = '';
        document.getElementById('periodSelect').value = 'day';
        document.getElementById('fulfillmentFilter').value = '';
        document.getElementById('dishSortBy').value = 'qty';
        document.getElementById('dishSortOrder').value = 'desc';
        
        this.loadAdvancedAnalytics();
        this.showAlert('All filters reset', 'info');
    }

    saveFilterPreset() {
        const preset = {
            fromDate: document.getElementById('fromDate')?.value,
            toDate: document.getElementById('toDate')?.value,
            period: document.getElementById('periodSelect')?.value,
            fulfillment: document.getElementById('fulfillmentFilter')?.value,
            dishSortBy: document.getElementById('dishSortBy')?.value,
            dishSortOrder: document.getElementById('dishSortOrder')?.value,
            savedAt: new Date().toISOString()
        };
        
        localStorage.setItem('analyticsFilterPreset', JSON.stringify(preset));
        this.showAlert('Filter preset saved successfully!', 'success');
    }

    loadFilterPreset() {
        const preset = localStorage.getItem('analyticsFilterPreset');
        if (preset) {
            try {
                const data = JSON.parse(preset);
                
                if (document.getElementById('fromDate')) document.getElementById('fromDate').value = data.fromDate || '';
                if (document.getElementById('toDate')) document.getElementById('toDate').value = data.toDate || '';
                if (document.getElementById('periodSelect')) document.getElementById('periodSelect').value = data.period || 'day';
                if (document.getElementById('fulfillmentFilter')) document.getElementById('fulfillmentFilter').value = data.fulfillment || '';
                if (document.getElementById('dishSortBy')) document.getElementById('dishSortBy').value = data.dishSortBy || 'qty';
                if (document.getElementById('dishSortOrder')) document.getElementById('dishSortOrder').value = data.dishSortOrder || 'desc';
                
                this.loadAnalyticsWithAdvancedFilters();
                this.showAlert(`Filter preset loaded (saved: ${new Date(data.savedAt).toLocaleString()})`, 'success');
                
            } catch (error) {
                this.showAlert('Error loading filter preset', 'danger');
            }
        } else {
            this.showAlert('No saved filter preset found', 'warning');
        }
    }

    async exportAnalyticsData() {
        try {
            const fromDate = document.getElementById('fromDate')?.value;
            const toDate = document.getElementById('toDate')?.value;

            // Get all analytics data
            const [summary, dishes, ordersByPeriod, repeatCustomers, marketing] = await Promise.all([
                this.apiCall(`/admin/analytics${fromDate || toDate ? `?${new URLSearchParams({...(fromDate && {from: fromDate}), ...(toDate && {to: toDate})}).toString()}` : ''}`),
                this.apiCall(`/admin/analytics/dish-popularity?limit=1000${fromDate ? `&from=${fromDate}` : ''}${toDate ? `&to=${toDate}` : ''}`),
                this.apiCall(`/admin/analytics/orders-by-period?period=day${fromDate ? `&from=${fromDate}` : ''}${toDate ? `&to=${toDate}` : ''}`),
                this.apiCall(`/admin/analytics/repeat-customers${fromDate || toDate ? `?${new URLSearchParams({...(fromDate && {from: fromDate}), ...(toDate && {to: toDate})}).toString()}` : ''}`),
                this.apiCall(`/admin/analytics/marketing-metrics${fromDate || toDate ? `?${new URLSearchParams({...(fromDate && {from: fromDate}), ...(toDate && {to: toDate})}).toString()}` : ''}`)
            ]);

            const exportData = {
                exportDate: new Date().toISOString(),
                period: { from: fromDate, to: toDate },
                summary,
                dishPopularity: dishes,
                ordersByPeriod,
                repeatCustomers,
                marketingMetrics: marketing
            };

            // Create and download JSON file
            const dataStr = JSON.stringify(exportData, null, 2);
            const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
            
            const exportFileDefaultName = `appetit_analytics_${fromDate || 'all'}_to_${toDate || 'now'}.json`;
            
            const linkElement = document.createElement('a');
            linkElement.setAttribute('href', dataUri);
            linkElement.setAttribute('download', exportFileDefaultName);
            linkElement.click();
            
            this.showAlert('Analytics data exported successfully!', 'success');

        } catch (error) {
            this.showAlert('Error exporting analytics data', 'danger');
        }
    }

    showMarketingMetricsModal() {
        const modalHtml = `
            <div class="modal fade" id="marketingMetricsModal" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Update Marketing Spend & Installs</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <form id="marketingUpdateForm">
                                <div class="row">
                                    <div class="col-md-6">
                                        <h6>Spend</h6>
                                        <div class="mb-3">
                                            <label class="form-label">Android Spend ($)</label>
                                            <input type="number" class="form-control" name="spend_android" step="0.01" value="0">
                                        </div>
                                        <div class="mb-3">
                                            <label class="form-label">iOS Spend ($)</label>
                                            <input type="number" class="form-control" name="spend_ios" step="0.01" value="0">
                                        </div>
                                        <div class="mb-3">
                                            <label class="form-label">Web Spend ($)</label>
                                            <input type="number" class="form-control" name="spend_web" step="0.01" value="0">
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <h6>Installs</h6>
                                        <div class="mb-3">
                                            <label class="form-label">Android Installs</label>
                                            <input type="number" class="form-control" name="installs_android" value="0">
                                        </div>
                                        <div class="mb-3">
                                            <label class="form-label">iOS Installs</label>
                                            <input type="number" class="form-control" name="installs_ios" value="0">
                                        </div>
                                        <div class="mb-3">
                                            <label class="form-label">Web Installs</label>
                                            <input type="number" class="form-control" name="installs_web" value="0">
                                        </div>
                                    </div>
                                </div>
                            </form>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                            <button type="button" class="btn btn-primary" onclick="app.updateMarketingMetrics()">Update</button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Remove existing modal if any
        const existingModal = document.getElementById('marketingMetricsModal');
        if (existingModal) {
            existingModal.remove();
        }

        // Add modal to page
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        new bootstrap.Modal(document.getElementById('marketingMetricsModal')).show();
    }

    async updateMarketingMetrics() {
        const form = document.getElementById('marketingUpdateForm');
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());

        // Convert to numbers
        Object.keys(data).forEach(key => {
            data[key] = parseFloat(data[key]) || 0;
        });

        try {
            await this.loadMarketingMetrics(); // Reload with new parameters
            bootstrap.Modal.getInstance(document.getElementById('marketingMetricsModal')).hide();
            this.showAlert('Marketing metrics updated successfully!', 'success');
        } catch (error) {
            // Error already shown in apiCall
        }
    }

    sortTable(sortField) {
        // Update sort controls and reload data
        if (document.getElementById('dishSortBy')) {
            document.getElementById('dishSortBy').value = sortField;
            
            // Toggle sort order
            const currentOrder = document.getElementById('dishSortOrder').value;
            document.getElementById('dishSortOrder').value = currentOrder === 'asc' ? 'desc' : 'asc';
            
            this.loadDishPopularity();
        }
    }

    viewDishDetails(dishId) {
        this.showAlert(`Dish details functionality - ID: ${dishId}`, 'info');
        // Could implement a detailed dish analytics view here
    }

    async checkIntegrations() {
        const statusDiv = document.getElementById('integrationStatus');
        statusDiv.innerHTML = '<div class="text-center"><div class="spinner-border" role="status"></div></div>';

        try {
            const status = await this.apiCall('/admin/integrations/status');
            
            const statusHtml = `
                <div class="row">
                    <div class="col-md-3">
                        <div class="card ${status.sms ? 'border-success' : 'border-danger'}">
                            <div class="card-body text-center">
                                <i class="bi bi-phone ${status.sms ? 'text-success' : 'text-danger'}" style="font-size: 2rem;"></i>
                                <h6 class="mt-2">SMS (Twilio)</h6>
                                <span class="badge bg-${status.sms ? 'success' : 'danger'}">${status.sms ? 'Connected' : 'Disconnected'}</span>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card ${status.email ? 'border-success' : 'border-danger'}">
                            <div class="card-body text-center">
                                <i class="bi bi-envelope ${status.email ? 'text-success' : 'text-danger'}" style="font-size: 2rem;"></i>
                                <h6 class="mt-2">Email (Resend)</h6>
                                <span class="badge bg-${status.email ? 'success' : 'danger'}">${status.email ? 'Connected' : 'Disconnected'}</span>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card ${status.push ? 'border-success' : 'border-danger'}">
                            <div class="card-body text-center">
                                <i class="bi bi-bell ${status.push ? 'text-success' : 'text-danger'}" style="font-size: 2rem;"></i>
                                <h6 class="mt-2">Push (FCM)</h6>
                                <span class="badge bg-${status.push ? 'success' : 'danger'}">${status.push ? 'Connected' : 'Disconnected'}</span>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card ${status.maps ? 'border-success' : 'border-danger'}">
                            <div class="card-body text-center">
                                <i class="bi bi-geo-alt ${status.maps ? 'text-success' : 'text-danger'}" style="font-size: 2rem;"></i>
                                <h6 class="mt-2">Maps (Google)</h6>
                                <span class="badge bg-${status.maps ? 'success' : 'danger'}">${status.maps ? 'Connected' : 'Disconnected'}</span>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            statusDiv.innerHTML = statusHtml;

        } catch (error) {
            statusDiv.innerHTML = `
                <div class="alert alert-danger">
                    <h6>✗ Integration Status Check Failed</h6>
                    <p>${error.message}</p>
                </div>
            `;
        }
    }


    getCartContent() {
        return `
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h2><i class="bi bi-cart"></i> Cart Management</h2>
                <div>
                    <button class="btn btn-primary" id="loadCartBtn">Load Cart</button>
                    <button class="btn btn-success" id="addToCartBtn">Add Menu Item</button>
                    <button class="btn btn-warning" id="clearCartBtn">Clear Cart</button>
                </div>
            </div>

            <div class="row">
                <div class="col-md-8">
                    <div class="card">
                        <div class="card-header"><h5>Cart Items</h5></div>
                        <div class="card-body" id="cartItemsList">
                            <p class="text-muted">Click "Load Cart" to see items</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card">
                        <div class="card-header"><h5>Cart Summary</h5></div>
                        <div class="card-body" id="cartSummary">
                            <p class="text-muted">Cart is empty</p>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    getPromoContent() {
        return `
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h2><i class="bi bi-tag"></i> Promocodes Management</h2>
                <div>
                    <button class="btn btn-primary" id="loadPromosBtn">Load Promocodes</button>
                    <button class="btn btn-success" id="createPromoBtn">Create Promocode</button>
                    <button class="btn btn-info" id="testPromoBtn">Test Promocode</button>
                </div>
            </div>

            <div class="row">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header"><h5>Promocodes List</h5></div>
                        <div class="card-body" id="promosList">
                            <p class="text-muted">Click "Load Promocodes" to see promocodes</p>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Create Promo Modal -->
            <div class="modal fade" id="createPromoModal" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Create Promocode</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <form id="createPromoForm">
                                <div class="mb-3">
                                    <label class="form-label">Code</label>
                                    <input type="text" class="form-control" name="code" required placeholder="DISCOUNT10">
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Type</label>
                                    <select class="form-select" name="kind" required>
                                        <option value="percent">Percentage</option>
                                        <option value="amount">Fixed Amount</option>
                                    </select>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Value</label>
                                    <input type="number" class="form-control" name="value" step="0.01" required>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Valid From</label>
                                    <input type="datetime-local" class="form-control" name="valid_from">
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Valid To</label>
                                    <input type="datetime-local" class="form-control" name="valid_to">
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Max Redemptions</label>
                                    <input type="number" class="form-control" name="max_redemptions" placeholder="Leave empty for unlimited">
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Per User Limit</label>
                                    <input type="number" class="form-control" name="per_user_limit" placeholder="Leave empty for unlimited">
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Minimum Subtotal</label>
                                    <input type="number" class="form-control" name="min_subtotal" step="0.01" placeholder="Leave empty for no minimum">
                                </div>
                                <div class="mb-3">
                                    <div class="form-check">
                                        <input type="checkbox" class="form-check-input" name="active" checked>
                                        <label class="form-check-label">Active</label>
                                    </div>
                                </div>
                            </form>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                            <button type="button" class="btn btn-primary" id="savePromoBtn">Create</button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Test Promo Modal -->
            <div class="modal fade" id="testPromoModal" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Test Promocode</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <form id="testPromoForm">
                                <div class="mb-3">
                                    <label class="form-label">Promo Code</label>
                                    <input type="text" class="form-control" name="code" required placeholder="Enter code to test">
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Test Subtotal</label>
                                    <input type="number" class="form-control" name="subtotal" step="0.01" value="50.00" required>
                                </div>
                            </form>
                            <div id="promoTestResult"></div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                            <button type="button" class="btn btn-primary" id="runPromoTestBtn">Test Code</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    getIntegrationsContent() {
        return `
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h2><i class="bi bi-gear"></i> Integrations Testing</h2>
            </div>

            <div class="row">
                <!-- SMS Testing -->
                <div class="col-md-6 mb-4">
                    <div class="card">
                        <div class="card-header"><h5><i class="bi bi-phone"></i> SMS Testing (Twilio)</h5></div>
                        <div class="card-body">
                            <form id="smsTestForm">
                                <div class="mb-3">
                                    <label class="form-label">Phone Number</label>
                                    <input type="tel" class="form-control" name="phone" placeholder="+1234567890" required>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Message</label>
                                    <textarea class="form-control" name="message" rows="3" placeholder="Test SMS message" required></textarea>
                                </div>
                                <button type="button" class="btn btn-primary" id="sendSmsBtn">Send SMS</button>
                            </form>
                        </div>
                    </div>
                </div>

                <!-- Email Testing -->
                <div class="col-md-6 mb-4">
                    <div class="card">
                        <div class="card-header"><h5><i class="bi bi-envelope"></i> Email Testing (Resend)</h5></div>
                        <div class="card-body">
                            <form id="emailTestForm">
                                <div class="mb-3">
                                    <label class="form-label">Email Address</label>
                                    <input type="email" class="form-control" name="email" placeholder="test@example.com" required>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Subject</label>
                                    <input type="text" class="form-control" name="subject" placeholder="Test Email" required>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Message</label>
                                    <textarea class="form-control" name="message" rows="3" placeholder="Test email content" required></textarea>
                                </div>
                                <button type="button" class="btn btn-primary" id="sendEmailBtn">Send Email</button>
                            </form>
                        </div>
                    </div>
                </div>

                <!-- Push Notifications -->
                <div class="col-md-6 mb-4">
                    <div class="card">
                        <div class="card-header"><h5><i class="bi bi-bell"></i> Push Notifications (FCM)</h5></div>
                        <div class="card-body">
                            <form id="pushTestForm">
                                <div class="mb-3">
                                    <label class="form-label">Title</label>
                                    <input type="text" class="form-control" name="title" placeholder="Notification Title" required>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Body</label>
                                    <textarea class="form-control" name="body" rows="2" placeholder="Notification message" required></textarea>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Target</label>
                                    <select class="form-select" name="target" required>
                                        <option value="all">All Users</option>
                                        <option value="test">Test Device</option>
                                    </select>
                                </div>
                                <button type="button" class="btn btn-primary" id="sendPushBtn">Send Push</button>
                            </form>
                            
                            <hr>
                            
                            <h6>Device Registration</h6>
                            <form id="deviceRegisterForm">
                                <div class="mb-3">
                                    <label class="form-label">FCM Token</label>
                                    <textarea class="form-control" name="fcm_token" rows="3" placeholder="Paste FCM token here"></textarea>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Platform</label>
                                    <select class="form-select" name="platform" required>
                                        <option value="web">Web</option>
                                        <option value="android">Android</option>
                                        <option value="ios">iOS</option>
                                    </select>
                                </div>
                                <button type="button" class="btn btn-success" id="registerDeviceBtn">Register Device</button>
                            </form>
                        </div>
                    </div>
                </div>

                <!-- Geolocation Testing -->
                <div class="col-md-6 mb-4">
                    <div class="card">
                        <div class="card-header"><h5><i class="bi bi-geo-alt"></i> Geolocation (Google Maps)</h5></div>
                        <div class="card-body">
                            <form id="geocodeTestForm">
                                <div class="mb-3">
                                    <label class="form-label">Address</label>
                                    <input type="text" class="form-control" name="address" placeholder="123 Main St, City, Country" required>
                                </div>
                                <button type="button" class="btn btn-primary" id="geocodeBtn">Geocode Address</button>
                            </form>
                            
                            <div id="geocodeResult" class="mt-3"></div>
                            
                            <hr>
                            
                            <form id="reverseGeocodeForm">
                                <div class="row">
                                    <div class="col-6">
                                        <label class="form-label">Latitude</label>
                                        <input type="number" class="form-control" name="lat" step="any" placeholder="40.7128" required>
                                    </div>
                                    <div class="col-6">
                                        <label class="form-label">Longitude</label>
                                        <input type="number" class="form-control" name="lng" step="any" placeholder="-74.0060" required>
                                    </div>
                                </div>
                                <button type="button" class="btn btn-primary mt-2" id="reverseGeocodeBtn">Reverse Geocode</button>
                            </form>
                            
                            <div id="reverseGeocodeResult" class="mt-3"></div>
                        </div>
                    </div>
                </div>

                <!-- Integration Status -->
                <div class="col-12">
                    <div class="card">
                        <div class="card-header"><h5><i class="bi bi-activity"></i> Integration Status</h5></div>
                        <div class="card-body">
                            <button class="btn btn-info" id="checkIntegrationsBtn">Check All Integrations</button>
                            <div id="integrationStatus" class="mt-3"></div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    getAnalyticsContent() {
        return `
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h2><i class="bi bi-graph-up"></i> Advanced Analytics Dashboard</h2>
                <div>
                    <button class="btn btn-primary" id="loadAnalyticsBtn">Load Analytics</button>
                    <button class="btn btn-success" id="loadAdvancedAnalyticsBtn">Load Advanced Analytics</button>
                    <button class="btn btn-info" id="testAnalyticsBtn">Test GA4 Event</button>
                    <button class="btn btn-warning" id="exportAnalyticsBtn">Export Data</button>
                </div>
            </div>

            <!-- Advanced Filters -->
            <div class="row mb-4">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <h5><i class="bi bi-funnel"></i> Advanced Filters & Controls</h5>
                        </div>
                        <div class="card-body">
                            <form id="advancedFilterForm" class="row g-3">
                                <div class="col-md-3">
                                    <label class="form-label">From Date</label>
                                    <input type="date" class="form-control" name="from_date" id="fromDate">
                                </div>
                                <div class="col-md-3">
                                    <label class="form-label">To Date</label>
                                    <input type="date" class="form-control" name="to_date" id="toDate">
                                </div>
                                <div class="col-md-2">
                                    <label class="form-label">Period</label>
                                    <select class="form-select" name="period" id="periodSelect">
                                        <option value="day">Daily</option>
                                        <option value="week">Weekly</option>
                                        <option value="month">Monthly</option>
                                    </select>
                                </div>
                                <div class="col-md-2">
                                    <label class="form-label">Fulfillment</label>
                                    <select class="form-select" name="fulfillment" id="fulfillmentFilter">
                                        <option value="">All</option>
                                        <option value="delivery">Delivery</option>
                                        <option value="pickup">Pickup</option>
                                    </select>
                                </div>
                                <div class="col-md-2">
                                    <label class="form-label">&nbsp;</label>
                                    <div>
                                        <button type="button" class="btn btn-outline-primary w-100" id="filterAnalyticsBtn">Apply Filter</button>
                                    </div>
                                </div>
                            </form>
                            <div class="mt-2">
                                <button type="button" class="btn btn-outline-secondary btn-sm" id="resetFilterBtn">Reset All</button>
                                <button type="button" class="btn btn-outline-info btn-sm" id="saveFilterBtn">Save Filter</button>
                                <button type="button" class="btn btn-outline-success btn-sm" id="loadFilterBtn">Load Saved</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="row">
                <!-- Summary Cards -->
                <div class="col-md-3 mb-4">
                    <div class="card text-center">
                        <div class="card-body">
                            <h5 class="card-title">Total Orders</h5>
                            <h2 class="text-primary" id="totalOrders">-</h2>
                            <small class="text-muted" id="ordersChange">-</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-3 mb-4">
                    <div class="card text-center">
                        <div class="card-body">
                            <h5 class="card-title">Total Revenue</h5>
                            <h2 class="text-success" id="totalRevenue">-</h2>
                            <small class="text-muted" id="revenueChange">-</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-3 mb-4">
                    <div class="card text-center">
                        <div class="card-body">
                            <h5 class="card-title">Average Order</h5>
                            <h2 class="text-info" id="avgOrder">-</h2>
                            <small class="text-muted" id="avgChange">-</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-3 mb-4">
                    <div class="card text-center">
                        <div class="card-body">
                            <h5 class="card-title">Repeat Customers</h5>
                            <h2 class="text-warning" id="repeatCustomers">-</h2>
                            <small class="text-muted" id="repeatRate">-</small>
                        </div>
                    </div>
                </div>
            </div>

            <div class="row">
                <!-- Orders by Period Chart -->
                <div class="col-md-8 mb-4">
                    <div class="card">
                        <div class="card-header">
                            <div class="d-flex justify-content-between align-items-center">
                                <h5><i class="bi bi-bar-chart"></i> Orders by Period</h5>
                                <div class="btn-group btn-group-sm" role="group">
                                    <input type="radio" class="btn-check" name="chartPeriod" id="chartDay" value="day" checked>
                                    <label class="btn btn-outline-primary" for="chartDay">Day</label>
                                    <input type="radio" class="btn-check" name="chartPeriod" id="chartWeek" value="week">
                                    <label class="btn btn-outline-primary" for="chartWeek">Week</label>
                                    <input type="radio" class="btn-check" name="chartPeriod" id="chartMonth" value="month">
                                    <label class="btn btn-outline-primary" for="chartMonth">Month</label>
                                </div>
                            </div>
                        </div>
                        <div class="card-body">
                            <div id="ordersChart" class="text-center text-muted">
                                Click "Load Advanced Analytics" to see chart
                            </div>
                        </div>
                    </div>
                </div>

                <!-- UTM Sources Enhanced -->
                <div class="col-md-4 mb-4">
                    <div class="card">
                        <div class="card-header">
                            <h5><i class="bi bi-pie-chart"></i> UTM Sources</h5>
                        </div>
                        <div class="card-body">
                            <div id="utmSources">
                                <p class="text-muted">Click "Load Analytics" to see UTM data</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="row">
                <!-- Dish Popularity Analysis -->
                <div class="col-12 mb-4">
                    <div class="card">
                        <div class="card-header">
                            <div class="d-flex justify-content-between align-items-center">
                                <h5><i class="bi bi-award"></i> Dish Popularity Analysis</h5>
                                <div class="d-flex gap-2">
                                    <select class="form-select form-select-sm" id="dishSortBy" style="width: auto;">
                                        <option value="qty">Sort by Quantity</option>
                                        <option value="revenue">Sort by Revenue</option>
                                        <option value="avg_price">Sort by Avg Price</option>
                                        <option value="name">Sort by Name</option>
                                    </select>
                                    <select class="form-select form-select-sm" id="dishSortOrder" style="width: auto;">
                                        <option value="desc">Descending</option>
                                        <option value="asc">Ascending</option>
                                    </select>
                                    <button class="btn btn-sm btn-outline-primary" id="loadDishPopularityBtn">Update</button>
                                </div>
                            </div>
                        </div>
                        <div class="card-body">
                            <div class="table-responsive">
                                <table class="table table-striped table-hover">
                                    <thead>
                                        <tr>
                                            <th class="sortable" data-sort="name">
                                                Dish Name <i class="bi bi-arrow-down-up"></i>
                                            </th>
                                            <th class="sortable text-end" data-sort="qty">
                                                Quantity Sold <i class="bi bi-arrow-down-up"></i>
                                            </th>
                                            <th class="sortable text-end" data-sort="revenue">
                                                Revenue <i class="bi bi-arrow-down-up"></i>
                                            </th>
                                            <th class="sortable text-end" data-sort="avg_price">
                                                Avg Price <i class="bi bi-arrow-down-up"></i>
                                            </th>
                                            <th class="text-center">Actions</th>
                                        </tr>
                                    </thead>
                                    <tbody id="dishPopularityTable">
                                        <tr>
                                            <td colspan="5" class="text-center text-muted">Click "Load Advanced Analytics" to see dish popularity</td>
                                        </tr>
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="row">
                <!-- Marketing Metrics -->
                <div class="col-md-6 mb-4">
                    <div class="card">
                        <div class="card-header">
                            <h5><i class="bi bi-megaphone"></i> Marketing Metrics</h5>
                        </div>
                        <div class="card-body">
                            <div id="marketingMetrics">
                                <p class="text-muted">Click "Load Advanced Analytics" to see marketing data</p>
                            </div>
                            <button class="btn btn-sm btn-outline-primary" id="updateMarketingBtn">Update Spend/Installs</button>
                        </div>
                    </div>
                </div>

                <!-- Order Status Enhanced -->
                <div class="col-md-6 mb-4">
                    <div class="card">
                        <div class="card-header">
                            <h5><i class="bi bi-graph-down"></i> Order Status Distribution</h5>
                        </div>
                        <div class="card-body">
                            <div id="orderStatus">
                                <p class="text-muted">Click "Load Analytics" to see order status</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

                <!-- Recent Orders with UTM -->
                <div class="col-12">
                    <div class="card">
                        <div class="card-header"><h5>Recent Orders with UTM Data</h5></div>
                        <div class="card-body">
                            <div class="table-responsive">
                                <table class="table table-striped">
                                    <thead>
                                        <tr>
                                            <th>Order #</th>
                                            <th>Date</th>
                                            <th>Total</th>
                                            <th>UTM Source</th>
                                            <th>UTM Medium</th>
                                            <th>UTM Campaign</th>
                                            <th>GA Client ID</th>
                                        </tr>
                                    </thead>
                                    <tbody id="recentOrdersTable">
                                        <tr>
                                            <td colspan="7" class="text-center text-muted">Click "Load Analytics" to see recent orders</td>
                                        </tr>
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Test GA4 Event Modal -->
            <div class="modal fade" id="testGA4Modal" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Test GA4 Event</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <form id="ga4TestForm">
                                <div class="mb-3">
                                    <label class="form-label">Event Name</label>
                                    <select class="form-select" name="event_name" required>
                                        <option value="page_view">Page View</option>
                                        <option value="add_to_cart">Add to Cart</option>
                                        <option value="purchase">Purchase</option>
                                        <option value="begin_checkout">Begin Checkout</option>
                                        <option value="custom_event">Custom Event</option>
                                    </select>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Client ID</label>
                                    <input type="text" class="form-control" name="client_id" placeholder="GA4 Client ID">
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Custom Parameters (JSON)</label>
                                    <textarea class="form-control" name="parameters" rows="4" placeholder='{"currency": "USD", "value": 25.50}'></textarea>
                                </div>
                            </form>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                            <button type="button" class="btn btn-primary" id="sendGA4EventBtn">Send Event</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    getBannersContent() {
        return `
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h2><i class="bi bi-images"></i> Banner Management</h2>
                <div>
                    <button class="btn btn-primary" id="loadBannersBtn">Load Banners</button>
                    <button class="btn btn-success" id="createBannerBtn">Create Banner</button>
                </div>
            </div>

            <!-- Create/Edit Banner Form -->
            <div class="row mb-4">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <h5><i class="bi bi-plus-circle"></i> Create/Edit Banner</h5>
                        </div>
                        <div class="card-body">
                            <form id="bannerForm" class="row g-3">
                                <div class="col-md-6">
                                    <label class="form-label">Title</label>
                                    <input type="text" class="form-control" name="title" placeholder="Banner title" required>
                                </div>
                                <div class="col-md-6">
                                    <label class="form-label">Type</label>
                                    <select class="form-select" name="banner_type" required>
                                        <option value="promo">Promotional</option>
                                        <option value="info">Informational</option>
                                        <option value="event">Event</option>
                                    </select>
                                </div>
                                <div class="col-md-12">
                                    <label class="form-label">Description</label>
                                    <textarea class="form-control" name="description" rows="3" placeholder="Banner description"></textarea>
                                </div>
                                <div class="col-md-6">
                                    <label class="form-label">Image URL</label>
                                    <input type="url" class="form-control" name="image_url" placeholder="https://example.com/banner.webp">
                                </div>
                                <div class="col-md-6">
                                    <label class="form-label">Action URL</label>
                                    <input type="url" class="form-control" name="action_url" placeholder="https://example.com/action">
                                </div>
                                <div class="col-md-4">
                                    <label class="form-label">Start Date</label>
                                    <input type="datetime-local" class="form-control" name="start_date">
                                </div>
                                <div class="col-md-4">
                                    <label class="form-label">End Date</label>
                                    <input type="datetime-local" class="form-control" name="end_date">
                                </div>
                                <div class="col-md-4">
                                    <label class="form-label">Sort Order</label>
                                    <input type="number" class="form-control" name="sort_order" value="0" min="0">
                                </div>
                                <div class="col-12">
                                    <div class="form-check">
                                        <input class="form-check-input" type="checkbox" name="is_active" id="bannerActive" checked>
                                        <label class="form-check-label" for="bannerActive">Active</label>
                                    </div>
                                </div>
                                <div class="col-12">
                                    <button type="submit" class="btn btn-success">Save Banner</button>
                                    <button type="button" class="btn btn-secondary" id="clearBannerFormBtn">Clear Form</button>
                                </div>
                                <input type="hidden" name="banner_id">
                            </form>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Banners List -->
            <div class="row">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <h5><i class="bi bi-list"></i> Banners List</h5>
                        </div>
                        <div class="card-body">
                            <div class="table-responsive">
                                <table class="table table-striped">
                                    <thead>
                                        <tr>
                                            <th>ID</th>
                                            <th>Title</th>
                                            <th>Type</th>
                                            <th>Image</th>
                                            <th>Status</th>
                                            <th>Start Date</th>
                                            <th>End Date</th>
                                            <th>Sort Order</th>
                                            <th>Actions</th>
                                        </tr>
                                    </thead>
                                    <tbody id="bannersTable">
                                        <tr>
                                            <td colspan="9" class="text-center text-muted">Click "Load Banners" to see banners</td>
                                        </tr>
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    getBusinessHoursContent() {
        return `
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h2><i class="bi bi-clock"></i> Business Hours Management</h2>
                <div>
                    <button class="btn btn-primary" id="loadBusinessHoursBtn">Load Current Hours</button>
                    <button class="btn btn-warning" id="emergencyCloseBtn">Emergency Close</button>
                    <button class="btn btn-success" id="emergencyOpenBtn">Emergency Open</button>
                </div>
            </div>

            <!-- Current Status -->
            <div class="row mb-4">
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header">
                            <h5><i class="bi bi-info-circle"></i> Current Status</h5>
                        </div>
                        <div class="card-body">
                            <div id="businessStatus">
                                <p class="text-muted">Click "Load Current Hours" to see status</p>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header">
                            <h5><i class="bi bi-clock-history"></i> Quick Actions</h5>
                        </div>
                        <div class="card-body">
                            <div class="d-grid gap-2">
                                <button class="btn btn-outline-primary" id="testOrderAcceptanceBtn">Test Order Acceptance</button>
                                <button class="btn btn-outline-info" id="getCurrentTimeBtn">Get Current Time</button>
                                <button class="btn btn-outline-secondary" id="checkAllDaysBtn">Check All Days</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Weekly Hours Management -->
            <div class="row">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <h5><i class="bi bi-calendar-week"></i> Weekly Hours</h5>
                        </div>
                        <div class="card-body">
                            <form id="weeklyHoursForm">
                                <div class="row" id="weeklyHoursContainer">
                                    <!-- Days will be populated here -->
                                </div>
                                <div class="mt-4">
                                    <button type="submit" class="btn btn-success">Save Weekly Hours</button>
                                    <button type="button" class="btn btn-secondary" id="resetWeeklyHoursBtn">Reset to Default</button>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Individual Day Editor -->
            <div class="row mt-4">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <h5><i class="bi bi-calendar-day"></i> Edit Individual Day</h5>
                        </div>
                        <div class="card-body">
                            <form id="singleDayForm" class="row g-3">
                                <div class="col-md-3">
                                    <label class="form-label">Day</label>
                                    <select class="form-select" name="day" required>
                                        <option value="monday">Monday</option>
                                        <option value="tuesday">Tuesday</option>
                                        <option value="wednesday">Wednesday</option>
                                        <option value="thursday">Thursday</option>
                                        <option value="friday">Friday</option>
                                        <option value="saturday">Saturday</option>
                                        <option value="sunday">Sunday</option>
                                    </select>
                                </div>
                                <div class="col-md-3">
                                    <label class="form-label">Open Time</label>
                                    <input type="time" class="form-control" name="open_time">
                                </div>
                                <div class="col-md-3">
                                    <label class="form-label">Close Time</label>
                                    <input type="time" class="form-control" name="close_time">
                                </div>
                                <div class="col-md-3 d-flex align-items-end">
                                    <div class="form-check me-3">
                                        <input class="form-check-input" type="checkbox" name="is_closed" id="dayClosedCheck">
                                        <label class="form-check-label" for="dayClosedCheck">Closed</label>
                                    </div>
                                    <button type="submit" class="btn btn-primary">Update Day</button>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
}

// Initialize the app when DOM is loaded
let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new AppetitTester();
});