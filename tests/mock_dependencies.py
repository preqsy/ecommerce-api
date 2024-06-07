from unittest.mock import MagicMock

from crud.auth import CRUDAuthUser
from crud.customer import CRUDCustomer


mock_crud_auth_user = MagicMock(spec=CRUDAuthUser)
mock_crud_customer = MagicMock(spec=CRUDCustomer)
