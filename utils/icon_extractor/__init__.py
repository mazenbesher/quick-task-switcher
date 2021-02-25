from pathlib import Path

from globals import config, paths
from utils.icon_extractor.extract_exe_icon import ExtractIcon


def get_icon(exe_path: str) -> Path:
    # cache dir
    icons_cache_dir = Path(config.json_config.icons_cache)
    if not icons_cache_dir.exists():
        icons_cache_dir.mkdir()

    # is cached?
    exe_name = Path(exe_path).name
    icon_path = Path(icons_cache_dir, f'{exe_name}.png')
    if icon_path.exists():
        return icon_path

    # extract
    extractor = ExtractIcon(exe_path)
    try:
        # windows "new" apps do not work!
        groups = extractor.get_group_icons()
    except ValueError:
        # TODO: fallback
        return paths.iconPaths.start

    # prefer icon with height 16 and 32 bit
    selected_icon_idx = -1
    for idx, icon in enumerate(groups[0]):
        if icon.Height == 16 and icon.BitCount == 32:
            selected_icon_idx = idx
            break

    if selected_icon_idx == -1:
        # try out 32
        for idx, icon in enumerate(groups[0]):
            if icon.Height == 32 and icon.BitCount == 32:
                selected_icon_idx = idx
                break

    if selected_icon_idx == -1:
        # select best one
        selected_icon_idx = extractor.best_icon(groups[0])

    # save
    im = extractor.export(groups[0], selected_icon_idx)
    im.save(icon_path)

    return icon_path
