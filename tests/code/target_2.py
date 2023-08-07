from uuid import uuid1


class UUIDUtil:
    @staticmethod
    def get_uuid():
        return uuid1()
