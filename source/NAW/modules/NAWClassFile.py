# NAW game class by SemD
from source.NAW.modules.NAWDataBase import NAWDataBase as GameData


class NAWGame:
    def __init__(self, id_user, variant = ''):
        self._idattr = id_user
        self._naw_db = GameData()
        self._user = self.user_data()
        self._user_message = variant

    def user_data(self):
        if self._naw_db.is_ok():
            return self._naw_db.get_user_data(self._idattr)
        return None
