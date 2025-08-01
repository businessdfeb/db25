import logging
import json
import traceback

logger = logging.getLogger(__name__)

class APILoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Information to log
        log_data = {
            'path': request.path,
            'method': request.method,
            'user': 'anonymous',
        }

        # Add user if authenticated
        if request.user.is_authenticated:
            log_data['user'] = request.user.username

        # Log request body for POST/PUT/PATCH
        if request.method in ['POST', 'PUT', 'PATCH'] and request.body:
            try:
                log_data['request_body'] = json.loads(request.body.decode('utf-8'))
            except json.JSONDecodeError:
                log_data['request_body'] = "Non-JSON body"

        response = self.get_response(request)

        # Log response status and body
        log_data['response_status'] = response.status_code
        if response.content and 'application/json' in response.get('Content-Type', ''):
             try:
                log_data['response_body'] = json.loads(response.content.decode('utf-8'))
             except json.JSONDecodeError:
                log_data['response_body'] = "Non-JSON body (error decoding)"

        logger.info(f"API Activity: {json.dumps(log_data, indent=2, sort_keys=True)}")

        return response
