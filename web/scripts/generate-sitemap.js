const fs = require('fs')

const pages = [
  { url: '', priority: '1.0', changefreq: 'weekly' },
  { url: 'blog', priority: '0.9', changefreq: 'daily' },
  { url: 'faq', priority: '0.7', changefreq: 'weekly' },
  { url: 'docs', priority: '0.6', changefreq: 'monthly' },
  { url: 'docs/getting-started', priority: '0.5', changefreq: 'monthly' },
  { url: 'docs/ocr-guide', priority: '0.5', changefreq: 'monthly' },
  { url: 'docs/telegram-bot', priority: '0.5', changefreq: 'monthly' },
  { url: 'legal/terms', priority: '0.4', changefreq: 'yearly' },
  { url: 'legal/privacy', priority: '0.4', changefreq: 'yearly' },
  { url: 'login', priority: '0.6', changefreq: 'monthly' },
]

const sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${pages.map(page => `  <url>
    <loc>https://jatuhtempo.up.railway.app/${page.url}</loc>
    <lastmod>2026-06-22</lastmod>
    <changefreq>${page.changefreq}</changefreq>
    <priority>${page.priority}</priority>
  </url>`).join('\n')}
</urlset>`

fs.writeFileSync('public/sitemap.xml', sitemap)
console.log('✅ sitemap.xml generated')
