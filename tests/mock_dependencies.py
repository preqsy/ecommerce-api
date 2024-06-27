from unittest.mock import MagicMock

from arq import ArqRedis

from crud import CRUDAuthUser, CRUDCustomer, CRUDProductImage, CRUDOtp


mock_crud_auth_user = MagicMock(spec=CRUDAuthUser)
mock_crud_customer = MagicMock(spec=CRUDCustomer)
mock_queue_connection = MagicMock(spec=ArqRedis)
mock_crud_product_image = MagicMock(spec=CRUDProductImage)
mock_crud_otp = MagicMock(spec=CRUDOtp)
