from core.conf.environ import env

if env("DEBUG"): 
    REST_FRAMEWORK = {
        "DEFAULT_AUTHENTICATION_CLASSES": [],
        "DEFAULT_PERMISSION_CLASSES": [],
        'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    }
else:  
    REST_FRAMEWORK = {
        'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    }


# Set up drf_spectacular, https://drf-spectacular.readthedocs.io/en/latest/settings.html
SPECTACULAR_SETTINGS = {
    'TITLE': 'DeNet Token API',
    'DESCRIPTION': 'API для работы с токенами в сети Polygon.',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}