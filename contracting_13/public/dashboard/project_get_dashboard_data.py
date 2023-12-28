

from frappe import _


def get_data(data={}):
    dash_data = data
    dash_data.transactions.append({"label": _("GL Entry"), "items": ["GL Entry"]},)
    dash_data.transactions.append({"label": _("Comparison"), "items": ["Comparison" , 
                                                            "Comparison Item Card" , "Comparison Item Log"]},)
    return dash_data