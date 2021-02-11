from utils.paths import resource_path


class IconsPaths:
    path_base = r'assets/tray_icon'
    start = resource_path(f'{path_base}/start.png')

    def desk(self, desk_num: int):
        return resource_path(f'{self.path_base}/desk{desk_num}.png')


iconPaths = IconsPaths()
