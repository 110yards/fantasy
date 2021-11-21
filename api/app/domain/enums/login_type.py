from enum import Enum


class LoginType(str, Enum):
    EMAIL = "email"
    GOOGLE = "google.com"
    FACEBOOK = "facebook.com"
    PASSWORD = "password"
