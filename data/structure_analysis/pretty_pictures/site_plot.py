class Site:
    'Stores properties to plot sites'
    def __init__(self, x, y, z, site_type, site_id, mix=False, yellow=False):
        self.position = [x, y, z]
        self.site_type = site_type
        self.site_id = site_id
        self.mix = mix
        self.yellow= yellow
        