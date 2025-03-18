from suntek_app.channel_partner import (
    setup_channel_partner_parent_warehouse,
    setup_channel_partner_parent_warehouse_type,
)
from suntek_app.migrate.toggle_solar_ambassador_integration_status import (
    toggle_solar_ambassador_integration,
)


def before_migrate():
    toggle_solar_ambassador_integration(enable=False)
    setup_channel_partner_parent_warehouse_type()
    setup_channel_partner_parent_warehouse()


def after_migrate():
    toggle_solar_ambassador_integration()
