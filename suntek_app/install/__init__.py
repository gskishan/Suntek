def before_install():
    from suntek_app.channel_partner import setup_channel_partner

    setup_channel_partner()
