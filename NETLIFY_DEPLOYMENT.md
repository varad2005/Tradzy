# Tradzy Frontend - Netlify Deployment Guide

## Project Structure

Your frontend is now ready for Netlify static hosting! All files have been updated with correct relative paths.

```
frontend/
├── index.html                  # Homepage
├── products.html               # Products page
├── login.html                  # Login/Signup page
├── contact.html                # Contact page
├── admin.html                  # Admin login
├── admin_dashboard.html        # Admin dashboard
├── retailer.html               # Retailer login
├── retailer_dashboard.html     # Retailer dashboard
├── retailer_cart.html          # Shopping cart
├── retailer_orders.html        # Orders page
├── retailer_wishlist.html      # Wishlist page
├── wholesaler.html             # Wholesaler login
├── wholesaler_dashboard.html   # Wholesaler dashboard
├── 403.html                    # Forbidden error page
├── 404.html                    # Not found error page
├── 500.html                    # Server error page
├── _redirects                  # Netlify redirects configuration
└── static/
    ├── style.css               # Main stylesheet
    ├── admin.css               # Admin styles
    ├── retailer.css            # Retailer styles
    └── api.js                  # API functions
```

## Deployment Steps

### Option 1: Deploy via Netlify CLI

1. Install Netlify CLI:
   ```bash
   npm install -g netlify-cli
   ```

2. Login to Netlify:
   ```bash
   netlify login
   ```

3. Deploy from the root directory:
   ```bash
   netlify deploy --dir=frontend --prod
   ```

### Option 2: Deploy via Netlify Dashboard

1. Go to [Netlify](https://app.netlify.com/)
2. Click "Add new site" → "Deploy manually"
3. Drag and drop the `frontend` folder
4. Your site will be live in seconds!

### Option 3: Connect to Git Repository

1. Push your code to GitHub/GitLab/Bitbucket
2. Go to Netlify Dashboard
3. Click "Add new site" → "Import an existing project"
4. Select your repository
5. Configure build settings:
   - **Build command:** Leave empty (no build needed)
   - **Publish directory:** `frontend`
6. Click "Deploy site"

## What Was Changed

All file paths have been updated to work with static hosting:

### CSS and JS Paths
- ❌ Old: `/static/style.css`
- ✅ New: `static/style.css`

### Navigation Links
- ❌ Old: `href="/products"`
- ✅ New: `href="products.html"`

### Internal Links
All internal navigation links now point to `.html` files:
- `/` → `index.html`
- `/products` → `products.html`
- `/login` → `login.html`
- `/contact` → `contact.html`
- `/admin` → `admin.html`
- `/retailer` → `retailer.html`
- `/wholesaler` → `wholesaler.html`
- And all dashboard pages

## Important Notes

### API Integration
If your site needs to connect to a backend API:

1. **Update API endpoints** in `static/api.js`
2. **Set up CORS** on your backend server
3. **Use environment variables** for API URLs in Netlify:
   - Go to Site settings → Environment variables
   - Add `API_URL` with your backend URL
   - Update `api.js` to use this variable

### Custom Domain
To add a custom domain:
1. Go to Site settings → Domain management
2. Click "Add custom domain"
3. Follow the DNS configuration instructions

### Environment Variables
If you need environment variables:
1. Go to Site settings → Environment variables
2. Add your variables (e.g., `API_URL`, `API_KEY`)
3. Access them in your JavaScript code

## Testing Locally

You can test the static site locally using:

### Python
```bash
cd frontend
python -m http.server 8000
```

### Node.js (http-server)
```bash
npm install -g http-server
cd frontend
http-server
```

### VS Code Live Server Extension
1. Install "Live Server" extension
2. Right-click on `index.html`
3. Select "Open with Live Server"

## File Structure for Netlify

The `netlify.toml` file in the root directory tells Netlify:
- Publish directory: `frontend`
- No build command needed
- Redirect all requests to index.html (for client-side routing)

## Troubleshooting

### 404 Errors on Page Refresh
- Make sure `_redirects` file exists in the `frontend` folder
- It should contain: `/*    /index.html   200`

### CSS Not Loading
- Check that paths are relative: `static/style.css`
- Not absolute: `/static/style.css`

### Links Not Working
- All links should end with `.html`
- Example: `href="products.html"` not `href="/products"`

## Next Steps

1. ✅ All HTML files updated with correct paths
2. ✅ CSS and JS paths fixed
3. ✅ Netlify configuration files created
4. 🚀 Ready to deploy!

Simply upload the `frontend` folder to Netlify and your site will be live!

---

**Need help?** Check the [Netlify Documentation](https://docs.netlify.com/)
