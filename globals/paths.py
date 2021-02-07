class IconsPaths:
    path_base = r'assets/tray_icon'
    start = f'{path_base}/start.png'

    def desk(self, desk_num: int):
        return f'{self.path_base}/desk{desk_num}.png'


iconPaths = IconsPaths()
