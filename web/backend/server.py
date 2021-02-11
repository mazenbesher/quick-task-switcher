import threading
import webbrowser

import uvicorn

from globals import config
from utils import ports
from web.backend.app import app


class Server(uvicorn.Server):
    """
    https://stackoverflow.com/a/64521239/1617883
    """

    def __init__(self):
        """
        https://www.uvicorn.org/deployment/#running-programmatically
        """
        # get free port and assign it in global config
        if not ports.is_port_open(config.backend_port):
            raise ValueError(f'Can not allocate port: {config.backend_port}')

        super(Server, self).__init__(uvicorn.Config(app,
                                                    host="127.0.0.1",
                                                    port=config.backend_port,
                                                    loop="asyncio",
                                                    log_level="info"))

    def install_signal_handlers(self):
        pass

    def run_in_thread(self):
        """
        https://github.com/encode/uvicorn/issues/742#issuecomment-674411676
        """
        self.thread = threading.Thread(target=self.run)
        self.thread.start()

    def stop(self):
        self.should_exit = True
        self.thread.join()

    def open_docs(self, redoc: bool = False):
        docs_version = "redoc" if redoc else "docs"
        docs_addr = f'http://127.0.0.1:{config.backend_port}/{docs_version}'
        webbrowser.open_new_tab(docs_addr)
