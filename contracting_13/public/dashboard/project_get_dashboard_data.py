

from frappe import _


def get_data(data={}):
    dash_data = data
    dash_data.transactions.append({"label": _("GL Entry"), "items": ["GL Entry"]},)
    return dash_data