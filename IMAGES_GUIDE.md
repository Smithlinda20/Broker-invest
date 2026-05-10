# Image Resources Guide for Broker Invest

## Recommended Image Sources

### Free High-Quality Stock Images

1. **Unsplash** - https://unsplash.com
   - Perfect for finance and crypto images
   - Search: "cryptocurrency", "investing", "trading", "business"
   - License: Free to use, no attribution required

2. **Pexels** - https://pexels.com
   - Great for professional business images
   - Search: "investment", "financial", "growth", "money"
   - License: Free, CC0

3. **Pixabay** - https://pixabay.com
   - Excellent collection of financial images
   - Search: "crypto trading", "stock market", "wealth"
   - License: Free, can be used commercially

4. **Freepik** - https://freepik.com
   - Professional design resources
   - Vectors and illustrations
   - Some free, some require credits

## Images to Download

Save these in `frontend/static/images/` folder:

### Homepage/Hero Section
1. **hero-background.jpg** (1920x1080)
   - Download from: Unsplash search "cryptocurrency market"
   - Use for: Hero section background

2. **chart-hero.jpg** (1200x600)
   - Download from: Unsplash search "stock market graph"
   - Use for: Chart animation/display

3. **investment-hero.png** (1200x800)
   - Download from: Pexels search "financial growth"
   - Use for: Hero image section

### Features Section
4. **security-icon.png** (256x256)
   - Download from: Pixabay search "security lock"
   - Use for: Security feature icon

5. **fast-icon.png** (256x256)
   - Download from: Pixabay search "lightning fast"
   - Use for: Speed/fast feature icon

6. **returns-icon.png** (256x256)
   - Download from: Pixabay search "profit growth"
   - Use for: High returns feature icon

7. **referral-icon.png** (256x256)
   - Download from: Pixabay search "people network"
   - Use for: Referral program icon

### Dashboard/User Section
8. **dashboard-hero.jpg** (1200x600)
   - Download from: Unsplash search "dashboard interface"
   - Use for: Dashboard background

9. **portfolio-icon.png** (256x256)
   - Download from: Pixabay search "portfolio"
   - Use for: Portfolio section

### Branding
10. **logo.png** (200x200)
    - Create or download: Company logo
    - Use for: Navigation bar, favicon

11. **logo-dark.png** (200x200)
    - Dark version of logo
    - Use for: Dark theme sections

### Cryptocurrency Specific
12. **bitcoin-icon.svg** or **.png** (256x256)
    - Available on: Pixabay, Unsplash
    - Use for: BTC payment option

13. **ethereum-icon.svg** or **.png** (256x256)
    - Available on: Pixabay, Unsplash
    - Use for: ETH payment option

14. **usdt-icon.svg** or **.png** (256x256)
    - Available on: Pixabay, Unsplash
    - Use for: USDT payment option

## How to Add Images

### Step 1: Download Images
1. Visit one of the image sources above
2. Search for appropriate keywords
3. Download at appropriate resolution
4. Save with descriptive names

### Step 2: Place in Folders
```
frontend/static/images/
├── hero/
│   ├── hero-background.jpg
│   ├── chart-hero.jpg
│   └── investment-hero.png
├── icons/
│   ├── security-icon.png
│   ├── fast-icon.png
│   ├── returns-icon.png
│   └── referral-icon.png
├── crypto/
│   ├── bitcoin-icon.png
│   ├── ethereum-icon.png
│   └── usdt-icon.png
├── branding/
│   ├── logo.png
│   └── logo-dark.png
└── dashboard/
    ├── dashboard-hero.jpg
    └── portfolio-icon.png
```

### Step 3: Update HTML References

In `index.html`:
```html
<!-- Hero Section -->
<div class="hero-image">
    <img src="/static/images/hero/investment-hero.png" alt="Investment">
</div>

<!-- Features Section -->
<div class="feature-card">
    <img src="/static/images/icons/security-icon.png" alt="Security" class="feature-image">
    <h3>Secure</h3>
</div>
```

In `dashboard.html`:
```html
<!-- Wallet Display -->
<div class="wallet-icon">
    <img src="/static/images/crypto/bitcoin-icon.png" alt="Bitcoin">
</div>
```

## Image Optimization Tips

1. **Compress Images**
   - Use online tools like TinyPNG or ImageOptim
   - Reduces file size, improves loading speed

2. **Use Appropriate Formats**
   - JPG: Photos and complex images
   - PNG: Icons and graphics with transparency
   - SVG: Logos and scalable graphics
   - WebP: Modern format for faster loading

3. **Responsive Sizes**
   - Desktop: 1920x1080 or larger
   - Tablet: 1024x768
   - Mobile: 512x384

## CSS for Background Images

```css
.hero {
    background-image: url('/static/images/hero/hero-background.jpg');
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}

.feature-icon img {
    width: 80px;
    height: 80px;
    object-fit: contain;
}
```

## Favicon Setup

Add to `<head>` in HTML:
```html
<link rel="icon" type="image/png" href="/static/images/branding/logo.png">
```

## Alternative: Using Placeholder Services (Temporary)

Until you download real images, use placeholder services:

```html
<!-- Temporary Placeholder -->
<img src="https://via.placeholder.com/1200x600/6366f1/ffffff?text=Investment+Platform" alt="Placeholder">

<!-- Using Unsplash Random Images (Temporary) -->
<img src="https://source.unsplash.com/1200x600/?cryptocurrency" alt="Random Crypto">
```

## Professional Image Collections by Category

### Investment/Finance
- "people", "business", "growth", "chart"
- Colors: Blues, Greens, Golds

### Cryptocurrency
- "bitcoin", "ethereum", "blockchain", "crypto"
- Colors: Orange (Bitcoin), Purple (Ethereum), Blue (USDT)

### Security
- "lock", "shield", "security", "protection"
- Colors: Green (trust), Blue (safety)

### User Dashboard
- "dashboard", "analytics", "chart", "interface"
- Colors: Professional blues, grays, accents

## Creating Custom Graphics

If you want to create your own graphics:
1. Use Figma (figma.com) - Free design tool
2. Use Canva (canva.com) - Easy drag-and-drop
3. Use Adobe Express (express.adobe.com) - Quick design

## Recommended Color Scheme

- Primary: #6366f1 (Indigo)
- Secondary: #8b5cf6 (Purple)
- Success: #10b981 (Green)
- Danger: #ef4444 (Red)
- Dark: #0f172a (Navy)

Images should complement these colors.

## File Size Guidelines

- Full-page images: 500KB - 2MB (compressed)
- Icons: 50KB - 200KB (PNG) or 10KB - 50KB (SVG)
- Thumbnails: 20KB - 100KB

## CDN Alternative

For better performance, consider hosting images on:
1. **Cloudinary** - Free tier with image optimization
2. **ImgIX** - High-performance image delivery
3. **AWS S3** - Cloud storage with CDN

Update image URLs accordingly.

## Quick Setup Command

```bash
# Create image directories
mkdir -p frontend/static/images/{hero,icons,crypto,branding,dashboard}

# Download sample images (using wget or curl)
cd frontend/static/images/

# Example for Unsplash images
wget https://source.unsplash.com/1200x600/?cryptocurrency -O hero/hero-background.jpg
```

---

**Remember**: Always check image licenses before use. Most images from these sources are free for commercial use, but verify the specific license.
