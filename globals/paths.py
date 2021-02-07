path_base = r'assets/tray_icon'


class IconsPaths:
    start = f'{path_base}/start.png'

    def desk(self, desk_num: int):
        return f'{path_base}/desk{desk_num}.png'


iconPaths = IconsPaths()
