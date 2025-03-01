from suntek_app.channel_partner import (
    setup_channel_partner,
    setup_channel_partner_parent_warehouse,
    setup_channel_partner_parent_warehouse_type,
)
from suntek_app.migrate.disable import solar_ambassador_integration
from suntek_app.migrate.enable import solar_ambassador_integration
from suntek_app.migrate.roles import create_sales_order_report_user


def before_migrate():
    solar_ambassador_integration()
    setup_channel_partner()
    setup_channel_partner_parent_warehouse_type()
    setup_channel_partner_parent_warehouse()
    create_sales_order_report_user()


def after_migrate():
    solar_ambassador_integration()
