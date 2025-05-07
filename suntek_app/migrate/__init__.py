from suntek_app.migrate.toggle_solar_ambassador_integration_status import (
    toggle_solar_ambassador_integration,
)


# from suntek_app.utils.permissions import remove_duplicate_permissions


def before_migrate():
    toggle_solar_ambassador_integration(enable=False)


def after_migrate():
    # remove_duplicate_permissions()
    toggle_solar_ambassador_integration()
