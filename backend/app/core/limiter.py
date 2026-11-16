"""Límite de peticiones por IP para frenar abuso en endpoints públicos."""
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
