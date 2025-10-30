# ✅ Deployment Checklist

## Pre-Deployment
- [x] All HTML files moved to frontend root
- [x] CSS paths updated from `/static/` to `static/`
- [x] JS paths updated from `/static/` to `static/`
- [x] Navigation links changed to `.html` files
- [x] `_redirects` file created
- [x] `netlify.toml` configured
- [x] Old templates folder removed

## Frontend Deployment to Netlify
- [ ] Deploy `frontend` folder to Netlify
- [ ] Verify homepage loads correctly
- [ ] Test all navigation links
- [ ] Check responsive design on mobile
- [ ] Test 404 error page
- [ ] Verify CSS and JS load properly
- [ ] Test forms (may need backend)

## Backend Deployment (Required for full functionality)
- [ ] Choose backend hosting platform
  - [ ] Heroku
  - [ ] Railway
  - [ ] Render
  - [ ] DigitalOcean
  - [ ] AWS/Azure
  - [ ] Other: _____________
- [ ] Deploy Flask backend
- [ ] Get backend URL
- [ ] Update `BASE_URL` in `frontend/static/api.js`
- [ ] Enable CORS on backend
- [ ] Test API endpoints work

## Backend CORS Configuration
```python
# Add to your Flask app.py
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=[
    'https://your-netlify-site.netlify.app',
    'http://localhost:8000'
])
```

## Testing
- [ ] Test login functionality
- [ ] Test product browsing
- [ ] Test cart operations
- [ ] Test wishlist
- [ ] Test order placement
- [ ] Test admin dashboard
- [ ] Test retailer dashboard
- [ ] Test wholesaler dashboard
- [ ] Test contact form

## Environment Variables (if needed)
- [ ] Add `API_URL` to Netlify environment variables
- [ ] Add any API keys required
- [ ] Add database connection strings (for backend)

## Security
- [ ] HTTPS enabled (automatic on Netlify)
- [ ] CORS properly configured
- [ ] API keys not exposed in frontend code
- [ ] JWT token handling secure
- [ ] Input validation on backend

## Performance
- [ ] Images optimized
- [ ] CSS minified (optional)
- [ ] JS minified (optional)
- [ ] CDN links working (Bootstrap, FontAwesome)

## Custom Domain (Optional)
- [ ] Purchase/use existing domain
- [ ] Add domain in Netlify settings
- [ ] Update DNS records
- [ ] Wait for SSL certificate
- [ ] Test custom domain

## Post-Deployment
- [ ] Test site on different browsers
  - [ ] Chrome
  - [ ] Firefox
  - [ ] Safari
  - [ ] Edge
- [ ] Test on different devices
  - [ ] Desktop
  - [ ] Tablet
  - [ ] Mobile
- [ ] Monitor Netlify deployment logs
- [ ] Set up Netlify forms (if using contact form)
- [ ] Configure Netlify analytics (optional)

## Documentation
- [ ] Update README with live URLs
- [ ] Document API endpoints
- [ ] Create user guide (optional)
- [ ] Document environment setup

## Maintenance
- [ ] Set up automatic deployments (Git integration)
- [ ] Monitor site uptime
- [ ] Check backend logs regularly
- [ ] Update dependencies periodically
- [ ] Backup database regularly (backend)

---

## Quick Deploy Commands

### Deploy Frontend
```bash
netlify deploy --dir=frontend --prod
```

### Deploy Backend (Example: Heroku)
```bash
cd backend
heroku create tradzy-api
git push heroku main
```

### Update API URL
```javascript
// In frontend/static/api.js
const BASE_URL = 'https://tradzy-api.herokuapp.com/api';
```

---

## Support Resources
- Netlify Status: https://www.netlifystatus.com/
- Netlify Community: https://answers.netlify.com/
- Flask Documentation: https://flask.palletsprojects.com/
- CORS Documentation: https://flask-cors.readthedocs.io/

---

**Status:** Ready for Deployment ✅  
**Last Updated:** $(Get-Date -Format "yyyy-MM-dd")
