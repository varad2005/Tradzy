// API Base URL
const BASE_URL = 'http://localhost:5000/api';

// Authentication Functions
async function login(username, password) {
    try {
        const response = await fetch(`${BASE_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include', // Important for cookies/session
            body: JSON.stringify({ username, password })
        });
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || 'Login failed');
        }
        
        // Store user role in localStorage for easy access
        localStorage.setItem('userRole', data.user.role);
        return data;
    } catch (error) {
        throw error;
    }
}

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

async function logout() {
    try {
        const response = await fetch(`${BASE_URL}/auth/logout`, {
            method: 'GET',
            credentials: 'include'
        });
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || 'Logout failed');
        }
        // Clear local storage
        localStorage.removeItem('userRole');
        return data;
    } catch (error) {
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