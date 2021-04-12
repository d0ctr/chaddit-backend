from ..models.role import RoleModel
from ..schemas.role import RoleSchema
class RoleId():
  # ser_roles = RoleSchema().dump(RoleModel.get_all(), many = True)
  # for role in ser_roles:
  #   if role.get('role_name') == 'ADMIN':
  #     ADMINISTRATOR = role.get('role_id')
  #   elif role.get('role_name') == 'MOD':
  #     MODERATOR = role.get('role_id')
  #   elif role.get('role_name') == 'USER':
  #     USER = role.get('role_id')
  ADMINISTRATOR = 1
  MODERATOR = 2
  USER = 3