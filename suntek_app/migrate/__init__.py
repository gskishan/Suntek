def before_migrate():
    from suntek_app.channel_partner import (
        setup_channel_partner,
        setup_channel_partner_parent_warehouse,
        setup_channel_partner_parent_warehouse_type,
    )
    from suntek_app.migrate.disable import solar_ambassador_integration

    setup_channel_partner()
    setup_channel_partner_parent_warehouse_type()
    setup_channel_partner_parent_warehouse()
    solar_ambassador_integration()


def after_migrate():
    from suntek_app.migrate.enable import solar_ambassador_integration

    solar_ambassador_integration()
