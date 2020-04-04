class SlugListConverter:
    
    regex = r'[a-z\d_+-]+'

    def to_python(self, url):
        return url.split('+')

    def to_url(self, obj):
        return '+'.join(obj)
