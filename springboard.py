import os
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from sanic import Sanic, response


class Springboard:
    def __init__(self, sanic: Sanic, frontend_dir: Path = Path('./frontend'),
                 add_html_routes: bool = True):
        self.sanic = sanic
        self._frontend = frontend_dir
        self.sanic.static('/', str(frontend_dir.absolute()))
        self.template_dict = {}

        self.env = Environment(
            loader=FileSystemLoader(str(frontend_dir.absolute())),
            autoescape=select_autoescape(['html', 'xml'])
        )

        # noinspection PyUnusedLocal
        async def index(request):
            return await response.file(
                str((frontend_dir / 'index.html').absolute()))

        self.sanic.add_route(index, '/')

        if add_html_routes:
            self._step_and_add_frontend_route(self._frontend)

    def localhost(self, port=80):
        """
        Starts running the Sanic app at localhost
        :param port: port to host the server through
        """
        print(
            f'Serving at http://localhost{":" if port == 80 else f":{port}"}')
        self.sanic.run(host='0.0.0.0', port=port)

    def _step_and_add_frontend_route(self, path: Path):
        """
        Recursive function that populates the app with paths that represent
        the html files in the frontend directory
        :param path: path to folder or file
        """
        for f in os.listdir(str(path.absolute())):
            full_path = path / f
            if full_path.is_dir() and not full_path.is_symlink():
                self._step_and_add_frontend_route(full_path)
            elif full_path.suffix.lower() == '.html':
                relative_path = full_path.relative_to(self._frontend)
                uri = relative_path.with_suffix('')

                # noinspection PyUnusedLocal
                async def resource(request):
                    template = self.env.get_template(str(full_path.absolute()))
                    return await response.html(
                        template.render(self.template_dict))

                self.sanic.add_route(resource, str(uri))
