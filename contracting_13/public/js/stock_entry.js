frappe.ui.form.on("Stock Entry", {
  refresh(frm) {
    frm.events.set_child_table_fields(frm);
    frm.events.comparison(frm);
  },
  setup: function (frm) {
    frappe.call({
      method:
        "contracting.contracting.doctype.stock_functions.fetch_contracting_data",
      callback: function (r) {
        if (r.message) {
        }
      },
    });
  },

  set_child_table_fields(frm) {
    frm.doc.items.forEach((e) => {
      var df = frappe.meta.get_docfield(
        "Stock Entry Detail",
        "comparison_item",
        e.name
      );
      df.hidden = !frm.doc.against_comparison;
    });

    frm.refresh_field("items");
  },

  against_comparison(frm) {
    if(frm.doc.against_comparison){
      frm.events.set_child_table_fields(frm);
    }
  },
  comparison: function (frm) {
    if (frm.doc.against_comparison && frm.doc.stock_entry_type) {
      frappe.call({
        method:
          "contracting.contracting.doctype.stock_functions.stock_entry_setup",
        args: {
          comparison: frm.doc.comparison,
        },
        callback: function (r) {
          if (r.message) {
            frm.set_query("comparison_item", function () {
              return {
                filters: [["item_code", "in", r.message]],
              };
            });
            frm.refresh_field("comparison_item");
            frm.set_query("comparison_item", "items", function () {
              return {
                filters: [["item_code", "in", r.message]],
              };
            });
            frm.refresh_field("items");
          }
        },
      });
    }

    frm.doc.items.forEach((e) => {
      var df = frappe.meta.get_docfield(
        "Stock Entry Detail",
        "comparison_item",
        e.name
      );
      df.get_query = function () {
        var filters = {
          comparison: frm.doc.comparison || "",
        };

        return {
          query:
            "contracting.contracting.doctype.stock_entry.stock_entry.get_item_query",
          filters: filters,
        };
      };
    });
  },
  stock_entry_type : function (frm){
    if(frm.doc.stock_entry_type){
      frm.events.filter_stock_entry_transfer(frm)
      frm.events.set_property_domain(frm)
    }
    // frm.events.set_field_property(frm)
  },
  set_property_domain:function(frm){
      frappe.call({
        method: "dynamic.api.get_active_domains",
        callback: function (r) {
            if (r.message && r.message.length) {
                if (r.message.includes("Contracting")) {
                  frappe.call({
                    'method': 'frappe.client.get_value',
                    'args': {
                      'doctype': 'Stock Entry Type',
                      'filters': {
                        'name': frm.doc.stock_entry_type
                      },
                       'fieldname':'purpose'
                    },
                    'callback': function(res){
                        frm.set_df_property("against_comparison", "hidden", ["Repack"].includes(res.message.purpose))
                        let re = ["Material Transfer", "Material Issue","Material Receipt"].includes(res.message.purpose)
                        console.log(`---------------${res}`)
                        frm.set_value("against_comparison", ["Material Transfer", "Material Issue","Material Receipt"].includes(res.message.purpose))
                        frm.refresh_field("against_comparison")
                    }
                  });
                  
                }
            }
        }
    })
      
    },
  comparison_item:function(frm){
    if(frm.doc.comparison_item){
      frappe.call({
        "method" : "contracting.contracting.doctype.stock_functions.get_comparision_items" ,
        args:{
          "comparison" : frm.doc.comparison,
          "item_code" : frm.doc.comparison_item,
        },
        callback :function(r){
          if (r.message){
            frm.clear_table("items")
            $.each(r.message || [], function(i, element) {
              let d = frappe.model.add_child(cur_frm.doc, "Stock Entry Detail", "items");
                d.item_code= element.item_code,
                d.item_name= element.item_name,
                d.basic_rate= element.unit_price,
                d.qty= element.total_qty,
                d.uom= element.uom,
                d.stock_uom= element.uom,
                d.transfer_qty= element.total_qty * element.conversion_factor,
                d.conversion_factor= element.conversion_factor
                // frm.events.get_item_details_custom(frm, d.doctype, d.name);
                // frm.events.set_basic_rate(frm, d.doctype, d.name);
            
            })
            
            frm.refresh_field("items")
          }
        } 
     
      })
    }
    

  },

  get_item_details_custom: function(frm, cdt, cdn) {
		// console.log('item_adds cstom')
		var d = locals[cdt][cdn];
		if(d.item_code) {
			var args_item_detail = {
				'item_code'			: d.item_code,
				'warehouse'			: cstr(d.s_warehouse) || cstr(d.t_warehouse),
				'transfer_qty'		: d.transfer_qty,
				'serial_no'		: d.serial_no,
				'bom_no'		: d.bom_no,
				'expense_account'	: d.expense_account,
				'cost_center'		: d.cost_center,
				'company'		: frm.doc.company,
				'qty'			: d.qty,
				'voucher_type'		: frm.doc.doctype,
				'voucher_no'		: d.name,
				'allow_zero_valuation': 1,
			};
      

      const args_get_incoming_rate = {
        'item_code'			: d.item_code,
        'posting_date'		: frm.doc.posting_date,
        'posting_time'		: frm.doc.posting_time,
        'warehouse'			: cstr(d.s_warehouse) || cstr(d.t_warehouse),
        'serial_no'			: d.serial_no,
        'company'			: frm.doc.company,
        'qty'				: d.s_warehouse ? -1*flt(d.transfer_qty) : flt(d.transfer_qty),
        'voucher_type'		: frm.doc.doctype,
        'voucher_no'		: d.name,
        'allow_zero_valuation': 1,
      };
      frm.call({
        doc: frm.doc,
        method:"get_item_stock_details",
        args:{
          args_item_detail:args_item_detail,
          args_get_incoming_rate:args_get_incoming_rate,
        },
        callback:function(r){
          // console.log(r.message)
          // console.log(`--->row==>${d.uom}`)
          d.uom = r.message.uom,
          // console.log(`--->row==>${d.uom}`)
          d.basic_rate = r.message.rate
          console.log(d)
          // frappe.model.set_value
          frm.refresh_field("items")
        }
      })
    }
  },

 
});



// frappe.ui.form.on("Stock Entry Detail", {

//   items_add:function(doc,cdt,cdn){

//   }

// })



