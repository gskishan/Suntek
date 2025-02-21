def before_migrate():
    from suntek_app.channel_partner import (
        setup_channel_partner,
        setup_channel_partner_parent_warehouse,
        setup_channel_partner_parent_warehouse_type,
    )

    setup_channel_partner()
    setup_channel_partner_parent_warehouse_type()
    setup_channel_partner_parent_warehouse()
