from cryptography.fernet import Fernet
from django.conf import settings
from django.db import models

class EncryptedTextField(models.TextField):
    """
    Stores text encrypted with Fernet; plain str in python, cipthertext in the DB.
    
    """


    
    def _fernet(self):

        try:
            fern = Fernet(settings.ENCRYPTION_KEY)
        except (ValueError, TypeError) as e:
            print(f"encryption_key is not properly formed")
            raise e

        return fern
    
    def get_prep_value(self, value):
        value = super().get_prep_value(value)
        if value is None:
            return None
        return self._fernet().encrypt(value.encode()).decode()
        
    def from_db_value(self, value, expression, connection):
        if value is None:
            return None
        return self._fernet().decrypt(value.encode()).decode()

# TODO: how is key rotation handled??
