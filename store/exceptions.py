from rest_framework.exceptions import APIException
from rest_framework import status

class ProductNotFoundException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Product not found.'
    default_code = 'product_not_found'

class CollectionNotFoundException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Collection not found.'
    default_code = 'collection_not_found'

class InvalidInventoryError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid inventory value.'
    default_code = 'invalid_inventory'

class DuplicateReviewError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'You have already reviewed this product.'
    default_code = 'duplicate_review'

class ProductDeletionError(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'Cannot delete product with existing orders.'
    default_code = 'product_deletion_error'
