// API Base URL - use relative path to work from any host
const BASE_URL = '/api';  // Works with localhost, 127.0.0.1, or IP address

/**
 * Login function - Sends credentials to backend and receives JWT token
 * @param {string} email - User's email or username
 * @param {string} password - User's password
 * @returns {Promise} Response data with token and user info
 */
async function login(email, password) {
    try {
        // Send POST request to login endpoint
        const response = await fetch(`${BASE_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include', // Include cookies for session support
            body: JSON.stringify({ email, password }) // Send email and password as JSON
        });
        
        // Parse the JSON response from server
        const data = await response.json();
        
        // Check if login was successful
        if (!response.ok) {
            // If not successful, throw error with message from server
            throw new Error(data.error || 'Login failed');
        }
        
        // Login successful! Store JWT token in localStorage
        // This token will be sent with future requests to authenticate the user
        if (data.access_token) {
            localStorage.setItem('jwt_token', data.access_token);
        }
        
        // Store user information in localStorage for easy access
        if (data.user) {
            localStorage.setItem('userRole', data.user.role);
            localStorage.setItem('userId', data.user.id);
            localStorage.setItem('username', data.user.username);
            localStorage.setItem('userEmail', data.user.email);
        }
        
        console.log('Login successful:', data.message);
        return data;
        
    } catch (error) {
        // Log error and re-throw for caller to handle
        console.error('Login error:', error.message);
        throw error;
    }
}

/**
 * Helper function to get JWT token from localStorage
 * @returns {string|null} JWT token or null if not found
 */
function getToken() {
    return localStorage.getItem('jwt_token');
}

/**
 * Helper function to check if user is logged in
 * @returns {boolean} True if JWT token exists
 */
function isLoggedIn() {
    return !!getToken();
}

/**
 * Example: Make authenticated API call with JWT token
 * This function shows how to include JWT token in Authorization header
 * @returns {Promise} Protected resource data
 */
async function getProtectedResource() {
    try {
        const token = getToken();
        
        if (!token) {
            throw new Error('No authentication token found. Please login first.');
        }
        
        // Make request with JWT token in Authorization header
        const response = await fetch(`${BASE_URL}/auth/protected`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}` // Include JWT token
            },
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            // If token is invalid or expired, clear it
            if (response.status === 401) {
                localStorage.removeItem('jwt_token');
                throw new Error('Session expired. Please login again.');
            }
            throw new Error(data.error || 'Failed to access protected resource');
        }
        
        return data;
        
    } catch (error) {
        console.error('Protected resource error:', error);
        throw error;
    }
}

// Authentication Functions (for backward compatibility)

async function register(username, password, email, role) {
    try {
        const response = await fetch(`${BASE_URL}/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password, email, role })
        });
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || 'Registration failed');
        }
        return data;
    } catch (error) {
        throw error;
    }
}

/**
 * Logout function - Clears JWT token and user data from localStorage
 * @returns {Promise} Response data
 */
async function logout() {
    try {
        // Call logout endpoint (optional - for server-side cleanup)
        const response = await fetch(`${BASE_URL}/auth/logout`, {
            method: 'GET',
            credentials: 'include'
        });
        const data = await response.json();
        
        // Clear all stored authentication data from localStorage
        localStorage.removeItem('jwt_token');
        localStorage.removeItem('userRole');
        localStorage.removeItem('userId');
        localStorage.removeItem('username');
        localStorage.removeItem('userEmail');
        
        console.log('Logout successful');
        return data;
        
    } catch (error) {
        // Even if server request fails, clear local data
        localStorage.removeItem('jwt_token');
        localStorage.removeItem('userRole');
        localStorage.removeItem('userId');
        localStorage.removeItem('username');
        localStorage.removeItem('userEmail');
        
        console.error('Logout error:', error);
        throw error;
    }
}

async function checkAuth() {
    try {
        const response = await fetch(`${BASE_URL}/auth/check-auth`, {
            method: 'GET',
            credentials: 'include'
        });
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || 'Authentication check failed');
        }
        // Update local storage
        if (data.authenticated) {
            localStorage.setItem('userRole', data.user.role);
        } else {
            localStorage.removeItem('userRole');
        }
        return data;
    } catch (error) {
        console.error('Login error:', error);
        throw error;
    }
}

async function register(username, password, email, role) {
    try {
        const response = await fetch(`${BASE_URL}/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify({ username, password, email, role })
        });
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || 'Registration failed');
        }
        return data;
    } catch (error) {
        console.error('Registration error:', error);
        throw error;
    }
}

async function logout() {
    try {
        const response = await fetch(`${BASE_URL}/logout`, {
            method: 'POST',
            credentials: 'include'
        });
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || 'Logout failed');
        }
        return data;
    } catch (error) {
        console.error('Logout error:', error);
        throw error;
    }
}

// Product Functions
async function getProducts() {
    try {
        const response = await fetch(`${BASE_URL}/products`, {
            credentials: 'include'
        });
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || 'Failed to fetch products');
        }
        return data;
    } catch (error) {
        console.error('Get products error:', error);
        throw error;
    }
}

async function addProduct(productData) {
    try {
        const response = await fetch(`${BASE_URL}/products`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify(productData)
        });
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || 'Failed to add product');
        }
        return data;
    } catch (error) {
        console.error('Add product error:', error);
        throw error;
    }
}

async function updateProduct(productId, productData) {
    try {
        const response = await fetch(`${BASE_URL}/products/${productId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify(productData)
        });
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || 'Failed to update product');
        }
        return data;
    } catch (error) {
        console.error('Update product error:', error);
        throw error;
    }
}

async function deleteProduct(productId) {
    try {
        const response = await fetch(`${BASE_URL}/products/${productId}`, {
            method: 'DELETE',
            credentials: 'include'
        });
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || 'Failed to delete product');
        }
        return data;
    } catch (error) {
        console.error('Delete product error:', error);
        throw error;
    }
}

// Admin Functions
async function getUsers() {
    try {
        const response = await fetch(`${BASE_URL}/admin/users`, {
            credentials: 'include'
        });
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || 'Failed to fetch users');
        }
        return data;
    } catch (error) {
        console.error('Get users error:', error);
        throw error;
    }
}

async function getStats() {
    try {
        const response = await fetch(`${BASE_URL}/admin/stats`, {
            credentials: 'include'
        });
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || 'Failed to fetch stats');
        }
        return data;
    } catch (error) {
        console.error('Get stats error:', error);
        throw error;
    }
}

async function deleteUser(userId) {
    try {
        const response = await fetch(`${BASE_URL}/admin/users/${userId}`, {
            method: 'DELETE',
            credentials: 'include'
        });
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || 'Failed to delete user');
        }
        return data;
    } catch (error) {
        console.error('Delete user error:', error);
        throw error;
    }
}