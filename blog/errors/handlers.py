from blog import app
from flask import render_template


@app.errorhandler(404)
def error_404(error):
    return render_template('errors/404.html', error=error)


@app.errorhandler(403)
def error_403(error):
    return render_template('errors/403.html', error=error)


@app.errorhandler(500)
def error_500(error):
    return render_template('errors/500.html', error=error)