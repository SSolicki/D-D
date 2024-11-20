from flask import render_template, request, jsonify
from app import db
from app.errors import bp
import logging
from logging.handlers import RotatingFileHandler
import os

# Configure logging
if not os.path.exists('logs'):
    os.mkdir('logs')
file_handler = RotatingFileHandler('logs/dnd_app.log', maxBytes=10240, backupCount=10)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
file_handler.setLevel(logging.INFO)
logging.getLogger('werkzeug').addHandler(file_handler)

def wants_json_response():
    return request.accept_mimetypes.best == 'application/json'

@bp.app_errorhandler(404)
def not_found_error(error):
    if wants_json_response():
        return jsonify({'error': 'Not found'}), 404
    return render_template('errors/404.html'), 404

@bp.app_errorhandler(500)
def internal_error(error):
    db.session.rollback()
    logging.error(f'Server Error: {error}')
    if wants_json_response():
        return jsonify({'error': 'Internal server error'}), 500
    return render_template('errors/500.html'), 500

@bp.app_errorhandler(403)
def forbidden_error(error):
    if wants_json_response():
        return jsonify({'error': 'Forbidden'}), 403
    return render_template('errors/403.html'), 403

@bp.app_errorhandler(429)
def ratelimit_error(error):
    if wants_json_response():
        return jsonify({'error': 'Rate limit exceeded'}), 429
    return render_template('errors/429.html'), 429

class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        super().__init__()
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv

@bp.app_errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    logging.warning(f'Invalid Usage: {error.message}')
    if wants_json_response():
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response
    return render_template('errors/400.html', error=error.message), 400

# Custom exception for campaign-related errors
class CampaignError(InvalidUsage):
    pass

# Custom exception for character-related errors
class CharacterError(InvalidUsage):
    pass

# Custom exception for inventory-related errors
class InventoryError(InvalidUsage):
    pass
