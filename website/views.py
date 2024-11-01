from flask import render_template
from website.baseView import baseView

class viewRoutes(baseView):
    def __init__(self, flaskApp):
        super().__init__(flaskApp)

    def _setupRoutes(self):
        @self._flaskApp.route("/home")
        def home():
            return render_template('home.html')
