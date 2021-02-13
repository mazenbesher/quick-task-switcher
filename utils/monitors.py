from typing import List, Tuple

import screeninfo


def is_loc_in_view(x: int, y: int) -> bool:
    monitors: List[screeninfo.Monitor] = screeninfo.get_monitors()
    for m in monitors:
        # is point in one of the monitors?
        if m.x < x < m.x + m.width and m.y < y < m.y + m.height:
            return True

    return False


def get_in_view_loc() -> Tuple[int, int]:
    """
    :return: (x, y)
    """
    first_monitor: screeninfo.Monitor = screeninfo.get_monitors()[0]
    return first_monitor.width // 2, first_monitor.height // 2


if __name__ == '__main__':
    # print(is_loc_in_view(1948, 974))
    # print(is_loc_in_view(3948, 974))
    print(get_in_view_loc())
