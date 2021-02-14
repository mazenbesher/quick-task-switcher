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

    @staticmethod
    def load_prev_durations_question():
        """
        :return: [Title, Message]
        """
        return [
            'Continue previous session',
            'Load durations from previous session?'
        ]

    @staticmethod
    def load_prev_durations_info():
        """
        :return: [Title, Message]
        """
        return [
            'Loaded previous durations',
            'Previous durations has been loaded',
        ]


messages = Messages()
