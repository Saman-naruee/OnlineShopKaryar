from urllib import response
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError

def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    if response is None:
        if isinstance(exc, ValidationError):
            response = Response(
                {
                    'error': 'Validation Error',
                    'detail': str(exc),
                    'code': 'validation_error',
                }, status=status.HTTP_400_BAD_REQUEST
            )
        
        elif isinstance(exc, IntegrityError):
            response = Response(
                {
                    'error': 'Integrity Error',
                    'detail': str(exc),
                    'code': 'integrity_error',
                }, status=status.HTTP_400_BAD_REQUEST
            )
        
        elif isinstance(exc, Exception):
            response = Response(
                {
                    'error': 'InternalServer Error',
                    'detail': str(exc),
                    'code': 'server_error',
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    # Customize the response format
    if response is not None:
        customized_response = {
            'success': False,
            'error': {
                'type': exc.__class__.__name__,
                'message': response.data.get('detail', str(exc)),
                'code': response.data.get('code', 'unknown_error'),
                'status': response.status_code
            }
        }
        response.data = customized_response
    
    return response
