from pedal.sandbox.mocked import MockModuleExposing, MethodExposer
from pedal.sandbox.mocked import MockModule
from pedal.utilities.system import IS_PYTHON_36


def friendly_urls(url: str) -> str:
    if url.strip("/") == "index":
        return "/"
    if not url.startswith('/'):
        url = '/' + url
    return url


class MockDrafter(MockModuleExposing):
    """
    Mock Drafter library that can be used to capture data from the students' program execution.
    """
    expose = MethodExposer()
    UNKNOWN_FUNCTIONS = []

    def __init__(self):
        super().__init__()
        self.original_routes = []
        self.routes = {}
        self._unknown_calls = []
        self.server_started = False

    def __repr__(self):
        return f"MockDrafter()"

    def __str__(self):
        return f"<MockDrafter()>"

    def add_route(self, url, func):
        self.original_routes.append((url, func))
        url = friendly_urls(url)
        self.routes[url] = func

    @expose
    def start_server(self):
        self.server_started = True

    @expose
    def show_debug_information(self):
        pass

    @expose
    def hide_debug_information(self):
        pass

    @expose
    def route(self, url: str = None):
        if callable(url):
            local_url = url.__name__
            self.add_route(local_url, url)
            return url

        def make_route(func):
            local_url = url
            if url is None:
                local_url = func.__name__
            self.add_route(local_url, func)
            return func

        return make_route

    @staticmethod
    def _load_drafter_component(name):

        def call_drafter_component(*args, **kwargs):
            import drafter
            return getattr(drafter, name)(*args, **kwargs)

        return call_drafter_component

    COMPONENTS = ['BulletedList', 'Button', 'CheckBox',
                  'Header', 'HorizontalRule', 'Image', 'LineBreak', 'Link', 'LinkContent',
                  'NumberedList', 'Page', 'PageContent', 'SelectBox',
                  'SubmitButton', 'Table', 'Text', 'TextArea', 'TextBox']
    for component in COMPONENTS:
        expose.add_with_name(_load_drafter_component(component), component)







"""
route, start_server
'show_debug_information', 
'hide_debug_information',
'route', 'start_server',
         
         'bold', 'change_background_color', 'change_border',
         'change_color', 'change_height', 'change_margin', 'change_padding', 'change_text_align',
         'change_text_decoration',
         'change_text_font', 'change_text_size', 'change_text_transform', 'change_width',
         'float_left',
         'float_right',  
         'italic', 
         'large_font', 'monospace',
         'small_font', 'strikethrough', 'underline',
         'update_attr', 'update_style']
"""