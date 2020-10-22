from utils.sitemaps import StaticSitemap, get_app_sitemaps


pages_sitemap = StaticSitemap(
    {
        'about': {}
    },
    priority = 0.5,
    changefreq = 'daily',
    protocol = 'https'
)

SITEMAPS = {
    'pages': pages_sitemap,
    **get_app_sitemaps()
}
