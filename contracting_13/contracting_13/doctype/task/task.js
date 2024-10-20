frappe.ui.form.on("Task", {
  setup: function (frm) {
    frm.set_query("comparison", function () {
      return {
        filters: {
          tender_status: ["in", ["Approved"]],
          docstatus: 1,
        },
      };
    });
    frm.set_query("sales_order", function () {
      return {
        filters: {
          comparison: ["in", [frm.doc.comparison]],
          project: ["in", [frm.doc.project]],
          docstatus: 1,
        },
      };
    });

    frm.fields_dict["items"].grid.get_field("state").get_query = function (
      doc,
      cdt,
      cdn
    ) {
      return {
        query:
          "contracting_13.contracting_13.doctype.clearance.clearance.comparsion_state_get_state_query",
        filters: { parent: doc.comparison },
      };
    };

    frm.fields_dict["items"].grid.get_field("item_code").get_query = function (
      doc,
      cdt,
      cdn
    ) {
      return {
        query:
          "contracting_13.contracting_13.doctype.stock_entry.stock_entry.get_item_query",
        filters: { comparison: doc.comparison },
      };
    };
  },
  refresh: function (frm) {
    if (frm.doc.comparison && frm.doc.sales_order) {
      frm.add_custom_button(
        __("Clearance"),
        function () {
          frappe.model.open_mapped_doc({
            method: "contracting_13.contracting_13.add_client_Sccript.make_task_clearence",
            frm: frm, //this.frm
          });
        },
        __("Create")
      );
    }
  },
});
