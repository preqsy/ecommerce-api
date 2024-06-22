from unittest.mock import MagicMock

from arq import ArqRedis

from crud import CRUDAuthUser, CRUDCustomer


mock_crud_auth_user = MagicMock(spec=CRUDAuthUser)
mock_crud_customer = MagicMock(spec=CRUDCustomer)
mock_queue_connection = MagicMock(spec=ArqRedis)
