from cryptography.fernet import Fernet
from django.conf import settings
from django.db import models

def _fernet():

        try:
            fern = Fernet(settings.ENCRYPTION_KEY)
        except (ValueError, TypeError) as e:
            print(f"encryption_key is not properly formed")
            raise e

        return fern

class EncryptedValue(str):
    """Ciphertext as loaded from the DB. Call .decrypt() to get the plain text."""

    def decrypt(self):
        return _fernet().decrypt(self.encode()).decode()

class EncryptedTextField(models.TextField):
    """
    Stores text encrypted with Fernet; plain str in python, cipthertext in the DB.
    
    """

    def get_prep_value(self, value):
        value = super().get_prep_value(value)
        if value is None:
            return None
        return _fernet().encrypt(value.encode()).decode()
        
    def from_db_value(self, value, expression, connection):
        if value is None:
            return None
        return EncryptedValue(value)

# TODO: handle key rotation