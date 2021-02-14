from .config import config


class Messages:
    @staticmethod
    def unsupported_desktops():
        """
        :return: [Title, Message]
        """
        return [
            "Exceeded supported number of desktops",
            f"Only {config.json_config.desktops_number} desktops are supported."
            f"The app will quit."
        ]

    @staticmethod
    def timer_fallback():
        """
        :return: [Title, Message]
        """
        return [
            "Warning",
            "Can not register registry callbacks"
        ]


messages = Messages()
