from utils.sitemaps import StaticSitemap, get_app_sitemaps


pages_sitemap = StaticSitemap(
    {
        'about': {}
    },
    priority = 0.5,
    changefreq = 'daily',
    protocol = 'https',
    i18n = True
)

SITEMAPS = {
    'pages': pages_sitemap,
    **get_app_sitemaps()
}
