from rest_framework.exceptions import APIException
from rest_framework import status

class ProductNotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Product not found.'
    default_code = 'product_not_found'

class CollectionNotFoundError(APIException):
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

class InvalidOrderException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid order.'
    default_code = 'invalid_order'

class InsufficientStockError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Insufficient stock available.'
    default_code = 'insufficient_stock'

class CartNotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Shopping cart not found.'
    default_code = 'cart_not_found'

class CartItemNotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Cart item not found.'
    default_code = 'cart_item_not_found'

class PaymentFailedError(APIException):
    status_code = status.HTTP_402_PAYMENT_REQUIRED
    default_detail = 'Payment processing failed.'
    default_code = 'payment_failed'

class OrderNotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Order not found.'
    default_code = 'order_not_found'

class UnauthorizedOrderAccessError(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'You are not authorized to access this order.'
    default_code = 'unauthorized_order_access'

class InvalidDiscountCodeError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid or expired discount code.'
    default_code = 'invalid_discount_code'

class CategoryNotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Category not found.'
    default_code = 'category_not_found'

class ProductOutOfStockError(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'Product is currently out of stock.'
    default_code = 'product_out_of_stock'
