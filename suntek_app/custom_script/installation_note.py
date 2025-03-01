from suntek_app.channel_partner.doctype.channel_partner.channel_partner import (
    get_channel_partner_data_from_project,
)


def set_channel_partner_data(doc, method):
    if doc.custom_project:
        doc.custom_channel_partner = get_channel_partner_data_from_project(
            doc.custom_project
        )
