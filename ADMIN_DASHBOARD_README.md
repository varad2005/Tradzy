# Admin Dashboard - TRADZY B2B Platform

## ✨ Overview
A clean, minimal, and modern admin dashboard for managing the B2B e-commerce platform connecting wholesalers and retailers.

## 🎨 Design Features

### Layout
- **Left Sidebar Navigation** (260px fixed width)
  - Dashboard
  - Wholesalers
  - Retailers
  - Orders

- **Top Bar** (70px height)
  - Search box with icon
  - Notifications bell with badge counter
  - Profile dropdown with admin info

- **Main Content Area**
  - Responsive card-based layout
  - Clean tables with hover effects
  - Plenty of white space and rounded corners

### Color Scheme
- **Primary Color**: Blue (#3b82f6)
- **Background**: Light gray (#f8fafc)
- **Text**: Dark slate (#1e293b)
- **Borders**: Light gray (#e2e8f0)
- **Status Badges**: Green (Active), Yellow (Pending), Blue (Completed), Red (Suspended)

## 📊 Dashboard Sections

### 1. Dashboard Overview
**Stats Cards:**
- Total Wholesalers (Blue icon)
- Total Retailers (Green icon)
- Total Orders (Purple icon)
- Total Revenue (Orange icon)

**Recent Activity Feed:**
- New wholesaler registrations
- Order placements
- New retailer signups
- Timestamps for each activity

### 2. Wholesalers Page
**Table Columns:**
- Name
- Company
- Products Count
- Status (Active/Suspended badge)
- Actions (View, Suspend/Activate buttons)

**Features:**
- Clean table design with alternating row hover
- Action buttons with icons
- Loading states

### 3. Retailers Page
**Table Columns:**
- Name
- Email
- Orders Count
- Status (Active/Suspended badge)
- Actions (View, Delete buttons)

**Features:**
- Similar clean table design
- Delete action with confirmation
- Responsive layout

### 4. Orders Page
**Table Columns:**
- Order ID
- Wholesaler Name
- Retailer Name
- Amount (₹ formatted)
- Status (Pending/Completed badge)
- Date

**Features:**
- Full order history view
- Color-coded status badges
- Date formatting

## 🔌 API Endpoints

### Statistics
```
GET /api/admin/stats
```
Returns: wholesalers count, retailers count, orders count, total revenue

### Wholesalers
```
GET /api/admin/wholesalers
```
Returns: List of all wholesalers with product counts

### Retailers
```
GET /api/admin/retailers
```
Returns: List of all retailers with order counts

### Orders
```
GET /api/admin/orders
```
Returns: All orders with wholesaler and retailer details

## 📱 Responsive Design
- Mobile-friendly layout
- Sidebar hidden on mobile (can be toggled)
- Responsive tables with horizontal scroll
- Adaptive grid for stats cards

## 🚀 Quick Start

1. **Start the server:**
   ```bash
   cd backend
   python app.py
   ```

2. **Access the dashboard:**
   - Open browser: `http://127.0.0.1:5000/admin`
   - Login with admin credentials
   - Explore the clean, minimal interface

## 💡 Key Features

✅ **Minimal & Clean** - No clutter, focused design
✅ **Single Page App** - JavaScript-based page switching
✅ **Real-time Data** - API-driven dynamic content
✅ **Status Badges** - Color-coded for quick scanning
✅ **Action Buttons** - View, Suspend, Delete with confirmations
✅ **Loading States** - Spinner indicators during data fetch
✅ **Error Handling** - Graceful fallbacks for failed requests
✅ **Hover Effects** - Subtle interactions for better UX
✅ **Rounded Cards** - Modern design with soft shadows
✅ **Icon Support** - Font Awesome icons throughout

## 🎯 Use Case
Perfect for a **clickable prototype** or **MVP** demonstration of a B2B e-commerce admin panel. The design prioritizes:
- Clarity over complexity
- Usability over fancy features
- Speed of comprehension
- Professional appearance

## 📝 Notes
- No complex graphs or charts (keeping it lightweight)
- Simple icon-based navigation
- Clean typography with Inter font
- Subtle shadows and borders
- Consistent spacing and alignment
- Mobile-responsive breakpoints at 768px

---

**Built for TRADZY B2B E-commerce Platform**
