/**
 * Resource Monitoring Dashboard for OpenPolicy Platform
 * Provides real-time resource usage monitoring and optimization insights
 */

class ResourceDashboard {
    constructor() {
        this.updateInterval = 5000; // 5 seconds
        this.resourceData = {};
        this.charts = {};
        this.init();
    }

    async init() {
        this.setupDashboard();
        this.startMonitoring();
        this.setupEventListeners();
    }

    setupDashboard() {
        const dashboard = document.getElementById('resource-dashboard');
        if (!dashboard) return;

        dashboard.innerHTML = `
            <div class="dashboard-header">
                <h1>🚀 OpenPolicy Platform Resource Dashboard</h1>
                <div class="status-indicator">
                    <span class="status-label">Cluster Status:</span>
                    <span id="cluster-status" class="status-value">Loading...</span>
                </div>
            </div>

            <div class="dashboard-grid">
                <!-- Resource Overview Cards -->
                <div class="resource-cards">
                    <div class="card memory-card">
                        <h3>💾 Memory Usage</h3>
                        <div class="metric">
                            <span id="memory-usage" class="value">--</span>
                            <span class="unit">Mi</span>
                        </div>
                        <div class="progress-bar">
                            <div id="memory-progress" class="progress-fill"></div>
                        </div>
                        <div class="details">
                            <span>Used: <span id="memory-used">--</span> Mi</span>
                            <span>Available: <span id="memory-available">--</span> Mi</span>
                        </div>
                    </div>

                    <div class="card cpu-card">
                        <h3>⚡ CPU Usage</h3>
                        <div class="metric">
                            <span id="cpu-usage" class="value">--</span>
                            <span class="unit">m</span>
                        </div>
                        <div class="progress-bar">
                            <div id="cpu-progress" class="progress-fill"></div>
                        </div>
                        <div class="details">
                            <span>Used: <span id="cpu-used">--</span> m</span>
                            <span>Available: <span id="cpu-available">--</span> m</span>
                        </div>
                    </div>

                    <div class="card services-card">
                        <h3>🔧 Services Status</h3>
                        <div class="metric">
                            <span id="services-running" class="value">--</span>
                            <span class="unit">/ 26</span>
                        </div>
                        <div class="service-breakdown">
                            <div class="status-item">
                                <span class="status-dot running"></span>
                                <span>Running: <span id="services-running-count">--</span></span>
                            </div>
                            <div class="status-item">
                                <span class="status-dot pending"></span>
                                <span>Pending: <span id="services-pending-count">--</span></span>
                            </div>
                            <div class="status-item">
                                <span class="status-dot failed"></span>
                                <span>Failed: <span id="services-failed-count">--</span></span>
                            </div>
                        </div>
                    </div>

                    <div class="card efficiency-card">
                        <h3>📊 Resource Efficiency</h3>
                        <div class="metric">
                            <span id="efficiency-score" class="value">--</span>
                            <span class="unit">%</span>
                        </div>
                        <div class="efficiency-details">
                            <div class="efficiency-item">
                                <span>Memory: <span id="memory-efficiency">--</span>%</span>
                            </div>
                            <div class="efficiency-item">
                                <span>CPU: <span id="cpu-efficiency">--</span>%</span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Resource Charts -->
                <div class="charts-section">
                    <div class="chart-container">
                        <h3>📈 Resource Usage Trends</h3>
                        <canvas id="resource-chart" width="400" height="200"></canvas>
                    </div>
                    
                    <div class="chart-container">
                        <h3>🔍 Service Resource Distribution</h3>
                        <canvas id="service-chart" width="400" height="200"></canvas>
                    </div>
                </div>

                <!-- Service Details Table -->
                <div class="services-table-section">
                    <h3>📋 Service Resource Details</h3>
                    <div class="table-controls">
                        <input type="text" id="service-search" placeholder="Search services..." class="search-input">
                        <select id="status-filter" class="filter-select">
                            <option value="all">All Status</option>
                            <option value="running">Running</option>
                            <option value="pending">Pending</option>
                            <option value="failed">Failed</option>
                        </select>
                    </div>
                    <div class="table-container">
                        <table id="services-table" class="services-table">
                            <thead>
                                <tr>
                                    <th>Service</th>
                                    <th>Status</th>
                                    <th>Memory Request</th>
                                    <th>Memory Limit</th>
                                    <th>CPU Request</th>
                                    <th>CPU Limit</th>
                                    <th>Replicas</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody id="services-table-body">
                                <!-- Service rows will be populated here -->
                            </tbody>
                        </table>
                    </div>
                </div>

                <!-- Resource Optimization Recommendations -->
                <div class="recommendations-section">
                    <h3>💡 Optimization Recommendations</h3>
                    <div id="recommendations-list" class="recommendations-list">
                        <!-- Recommendations will be populated here -->
                    </div>
                </div>
            </div>

            <!-- Real-time Updates Panel -->
            <div class="updates-panel">
                <h3>🔄 Real-time Updates</h3>
                <div id="updates-log" class="updates-log">
                    <!-- Update logs will be populated here -->
                </div>
            </div>
        `;

        this.setupCharts();
    }

    setupCharts() {
        // Resource Usage Trend Chart
        const resourceCtx = document.getElementById('resource-chart')?.getContext('2d');
        if (resourceCtx) {
            this.charts.resource = new Chart(resourceCtx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Memory Usage (Mi)',
                        data: [],
                        borderColor: 'rgb(75, 192, 192)',
                        backgroundColor: 'rgba(75, 192, 192, 0.2)',
                        tension: 0.1
                    }, {
                        label: 'CPU Usage (m)',
                        data: [],
                        borderColor: 'rgb(255, 99, 132)',
                        backgroundColor: 'rgba(255, 99, 132, 0.2)',
                        tension: 0.1
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        }

        // Service Resource Distribution Chart
        const serviceCtx = document.getElementById('service-chart')?.getContext('2d');
        if (serviceCtx) {
            this.charts.service = new Chart(serviceCtx, {
                type: 'doughnut',
                data: {
                    labels: ['Memory', 'CPU'],
                    datasets: [{
                        data: [0, 0],
                        backgroundColor: [
                            'rgba(54, 162, 235, 0.8)',
                            'rgba(255, 206, 86, 0.8)'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        }
                    }
                }
            });
        }
    }

    async startMonitoring() {
        // Initial data load
        await this.updateResourceData();
        
        // Set up periodic updates
        setInterval(async () => {
            await this.updateResourceData();
        }, this.updateInterval);
    }

    async updateResourceData() {
        try {
            // Fetch cluster resource data
            const clusterData = await this.fetchClusterResources();
            const servicesData = await this.fetchServicesData();
            
            this.resourceData = { ...clusterData, ...servicesData };
            this.updateDashboard();
            this.updateCharts();
            this.updateServicesTable();
            this.generateRecommendations();
            this.logUpdate('Resource data updated successfully');
        } catch (error) {
            console.error('Error updating resource data:', error);
            this.logUpdate(`Error updating data: ${error.message}`, 'error');
        }
    }

    async fetchClusterResources() {
        // Simulate API call to Kubernetes metrics
        // In production, this would call the Kubernetes API
        return {
            memory: {
                total: 8192,
                used: 7714,
                available: 478,
                percentage: 94.2
            },
            cpu: {
                total: 16000,
                used: 4250,
                available: 11750,
                percentage: 26.6
            }
        };
    }

    async fetchServicesData() {
        // Simulate API call to get services data
        // In production, this would call the Kubernetes API
        return {
            services: [
                {
                    name: 'api-gateway',
                    status: 'running',
                    memoryRequest: 128,
                    memoryLimit: 256,
                    cpuRequest: 50,
                    cpuLimit: 100,
                    replicas: 1
                },
                {
                    name: 'auth-service',
                    status: 'running',
                    memoryRequest: 128,
                    memoryLimit: 256,
                    cpuRequest: 50,
                    cpuLimit: 100,
                    replicas: 2
                }
                // More services would be populated here
            ]
        };
    }

    updateDashboard() {
        const data = this.resourceData;
        if (!data.memory || !data.cpu) return;

        // Update memory card
        document.getElementById('memory-usage').textContent = data.memory.used;
        document.getElementById('memory-used').textContent = data.memory.used;
        document.getElementById('memory-available').textContent = data.memory.available;
        
        const memoryProgress = document.getElementById('memory-progress');
        memoryProgress.style.width = `${data.memory.percentage}%`;
        memoryProgress.className = `progress-fill ${this.getProgressClass(data.memory.percentage)}`;

        // Update CPU card
        document.getElementById('cpu-usage').textContent = data.cpu.used;
        document.getElementById('cpu-used').textContent = data.cpu.used;
        document.getElementById('cpu-available').textContent = data.cpu.available;
        
        const cpuProgress = document.getElementById('cpu-progress');
        cpuProgress.style.width = `${data.cpu.percentage}%`;
        cpuProgress.className = `progress-fill ${this.getProgressClass(data.cpu.percentage)}`;

        // Update cluster status
        const clusterStatus = document.getElementById('cluster-status');
        clusterStatus.textContent = this.getClusterStatus(data.memory.percentage, data.cpu.percentage);
        clusterStatus.className = `status-value ${this.getStatusClass(data.memory.percentage, data.cpu.percentage)}`;

        // Update efficiency metrics
        document.getElementById('memory-efficiency').textContent = (100 - data.memory.percentage).toFixed(1);
        document.getElementById('cpu-efficiency').textContent = (100 - data.cpu.percentage).toFixed(1);
        
        const efficiencyScore = ((100 - data.memory.percentage) + (100 - data.cpu.percentage)) / 2;
        document.getElementById('efficiency-score').textContent = efficiencyScore.toFixed(1);
    }

    updateCharts() {
        const data = this.resourceData;
        if (!data.memory || !data.cpu) return;

        // Update resource trend chart
        if (this.charts.resource) {
            const now = new Date().toLocaleTimeString();
            this.charts.resource.data.labels.push(now);
            this.charts.resource.data.datasets[0].data.push(data.memory.used);
            this.charts.resource.data.datasets[1].data.push(data.cpu.used);

            // Keep only last 20 data points
            if (this.charts.resource.data.labels.length > 20) {
                this.charts.resource.data.labels.shift();
                this.charts.resource.data.datasets[0].data.shift();
                this.charts.resource.data.datasets[1].data.shift();
            }

            this.charts.resource.update();
        }

        // Update service distribution chart
        if (this.charts.service) {
            this.charts.service.data.datasets[0].data = [
                data.memory.used,
                data.cpu.used
            ];
            this.charts.service.update();
        }
    }

    updateServicesTable() {
        const data = this.resourceData;
        if (!data.services) return;

        const tbody = document.getElementById('services-table-body');
        if (!tbody) return;

        tbody.innerHTML = '';

        data.services.forEach(service => {
            const row = document.createElement('tr');
            row.className = `service-row ${service.status}`;
            
            row.innerHTML = `
                <td>${service.name}</td>
                <td>
                    <span class="status-badge ${service.status}">
                        ${service.status}
                    </span>
                </td>
                <td>${service.memoryRequest} Mi</td>
                <td>${service.memoryLimit} Mi</td>
                <td>${service.cpuRequest} m</td>
                <td>${service.cpuLimit} m</td>
                <td>${service.replicas}</td>
                <td>
                    <button class="action-btn" onclick="dashboard.restartService('${service.name}')">
                        🔄 Restart
                    </button>
                    <button class="action-btn" onclick="dashboard.scaleService('${service.name}')">
                        📏 Scale
                    </button>
                </td>
            `;
            
            tbody.appendChild(row);
        });

        // Update service counts
        const runningCount = data.services.filter(s => s.status === 'running').length;
        const pendingCount = data.services.filter(s => s.status === 'pending').length;
        const failedCount = data.services.filter(s => s.status === 'failed').length;

        document.getElementById('services-running-count').textContent = runningCount;
        document.getElementById('services-pending-count').textContent = pendingCount;
        document.getElementById('services-failed-count').textContent = failedCount;
        document.getElementById('services-running').textContent = runningCount;
    }

    generateRecommendations() {
        const data = this.resourceData;
        if (!data.memory || !data.cpu) return;

        const recommendations = [];
        const recommendationsList = document.getElementById('recommendations-list');
        if (!recommendationsList) return;

        // Memory-based recommendations
        if (data.memory.percentage > 90) {
            recommendations.push({
                type: 'critical',
                message: 'Memory usage is critically high. Consider reducing service replicas or optimizing resource requests.',
                action: 'Reduce memory requests from 256Mi to 128Mi for non-critical services'
            });
        } else if (data.memory.percentage > 80) {
            recommendations.push({
                type: 'warning',
                message: 'Memory usage is high. Monitor closely and consider optimization.',
                action: 'Review service resource allocation and reduce unnecessary replicas'
            });
        }

        // CPU-based recommendations
        if (data.cpu.percentage > 80) {
            recommendations.push({
                type: 'warning',
                message: 'CPU usage is high. Consider load balancing or scaling.',
                action: 'Implement horizontal pod autoscaling for high-CPU services'
            });
        }

        // Efficiency recommendations
        if (data.memory.percentage < 50 && data.cpu.percentage < 50) {
            recommendations.push({
                type: 'info',
                message: 'Resources are underutilized. Consider increasing service replicas for better performance.',
                action: 'Scale up services to improve performance and resource utilization'
            });
        }

        // Render recommendations
        recommendationsList.innerHTML = recommendations.map(rec => `
            <div class="recommendation ${rec.type}">
                <div class="recommendation-header">
                    <span class="recommendation-type">${rec.type.toUpperCase()}</span>
                    <span class="recommendation-message">${rec.message}</span>
                </div>
                <div class="recommendation-action">
                    <strong>Action:</strong> ${rec.action}
                </div>
            </div>
        `).join('');
    }

    getProgressClass(percentage) {
        if (percentage >= 90) return 'critical';
        if (percentage >= 80) return 'warning';
        if (percentage >= 60) return 'info';
        return 'success';
    }

    getStatusClass(memoryPercentage, cpuPercentage) {
        if (memoryPercentage >= 90 || cpuPercentage >= 90) return 'critical';
        if (memoryPercentage >= 80 || cpuPercentage >= 80) return 'warning';
        if (memoryPercentage >= 60 || cpuPercentage >= 60) return 'info';
        return 'success';
    }

    getClusterStatus(memoryPercentage, cpuPercentage) {
        if (memoryPercentage >= 90 || cpuPercentage >= 90) return 'CRITICAL';
        if (memoryPercentage >= 80 || cpuPercentage >= 80) return 'WARNING';
        if (memoryPercentage >= 60 || cpuPercentage >= 60) return 'HEALTHY';
        return 'OPTIMAL';
    }

    logUpdate(message, type = 'info') {
        const updatesLog = document.getElementById('updates-log');
        if (!updatesLog) return;

        const timestamp = new Date().toLocaleTimeString();
        const logEntry = document.createElement('div');
        logEntry.className = `log-entry ${type}`;
        logEntry.innerHTML = `
            <span class="log-timestamp">[${timestamp}]</span>
            <span class="log-message">${message}</span>
        `;

        updatesLog.insertBefore(logEntry, updatesLog.firstChild);

        // Keep only last 50 log entries
        while (updatesLog.children.length > 50) {
            updatesLog.removeChild(updatesLog.lastChild);
        }
    }

    async restartService(serviceName) {
        try {
            // In production, this would call the Kubernetes API
            this.logUpdate(`Restarting service: ${serviceName}`, 'info');
            // Simulate API call
            await new Promise(resolve => setTimeout(resolve, 1000));
            this.logUpdate(`Service ${serviceName} restarted successfully`, 'success');
        } catch (error) {
            this.logUpdate(`Failed to restart ${serviceName}: ${error.message}`, 'error');
        }
    }

    async scaleService(serviceName) {
        try {
            // In production, this would call the Kubernetes API
            this.logUpdate(`Scaling service: ${serviceName}`, 'info');
            // Simulate API call
            await new Promise(resolve => setTimeout(resolve, 1000));
            this.logUpdate(`Service ${serviceName} scaled successfully`, 'success');
        } catch (error) {
            this.logUpdate(`Failed to scale ${serviceName}: ${error.message}`, 'error');
        }
    }

    setupEventListeners() {
        // Service search functionality
        const searchInput = document.getElementById('service-search');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.filterServices(e.target.value);
            });
        }

        // Status filter functionality
        const statusFilter = document.getElementById('status-filter');
        if (statusFilter) {
            statusFilter.addEventListener('change', (e) => {
                this.filterServicesByStatus(e.target.value);
            });
        }
    }

    filterServices(searchTerm) {
        const rows = document.querySelectorAll('.service-row');
        rows.forEach(row => {
            const serviceName = row.cells[0].textContent.toLowerCase();
            if (serviceName.includes(searchTerm.toLowerCase())) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
    }

    filterServicesByStatus(status) {
        const rows = document.querySelectorAll('.service-row');
        rows.forEach(row => {
            if (status === 'all' || row.classList.contains(status)) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new ResourceDashboard();
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ResourceDashboard;
}
