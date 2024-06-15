from unittest.mock import MagicMock

from crud import CRUDAuthUser, CRUDCustomer


mock_crud_auth_user = MagicMock(spec=CRUDAuthUser)
mock_crud_customer = MagicMock(spec=CRUDCustomer)
