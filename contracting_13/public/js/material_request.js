frappe.ui.form.on("Material Request",{

  onload:function(frm) {
    frm.events.get_filters(frm)
  },
  setup:function(frm){
    frm.events.setup_comparsion_query(frm)
  },

  refresh:function(frm){
    frm.events.setup_comparsion_query(frm);
    // Hide standard Create button 
    frm.page.remove_inner_button('Create');
    // Make another Create_ Button to override the standard
    frm.events.make_custom_buttons(frm);
    // Check if the document is submitted
    if (frm.doc.docstatus == 1) {

      // Allow row selection (checkboxes) in the Items table
      frm.fields_dict['items'].grid.wrapper.find('input[type=checkbox]').prop('disabled', false);


      // Hide row delete and add buttons to prevent modifications
      frm.fields_dict['items'].grid.wrapper.find('.grid-remove-rows').hide();  // Hide the "remove all rows" button
      frm.fields_dict['items'].grid.wrapper.find('.grid-add-row').hide();      // Hide the "add row" button
      frm.fields_dict['items'].grid.wrapper.find('.grid-delete-row').hide();   // Hide individual row delete buttons
      
    }
  },

  make_custom_buttons: function(frm) {
		if (frm.doc.docstatus == 1 && frm.doc.status != 'Stopped') {
			let precision = frappe.defaults.get_default("float_precision");
			if (flt(frm.doc.per_ordered, precision) < 100) {

				if (frm.doc.material_request_type === "Purchase") {
					frm.add_custom_button(__('Purchase Order'),
						() => frm.events.make_purchase_order(frm), __('Create_'));
				}

				if (frm.doc.material_request_type === "Purchase") {
					frm.add_custom_button(__("Request for Quotation"),
						() => frm.events.make_request_for_quotation(frm), __('Create_'));
				}

				if (frm.doc.material_request_type === "Purchase") {
					frm.add_custom_button(__("Supplier Quotation"),
						() => frm.events.make_supplier_quotation(frm), __('Create_'));
				}

				frm.page.set_inner_btn_group_as_primary(__('Create_'));

			}
		}
  },

  make_purchase_order: function(frm) {
		frappe.prompt(
			{
				label: __('For Default Supplier (Optional)'),
				fieldname:'default_supplier',
				fieldtype: 'Link',
				options: 'Supplier',
				description: __('Select a Supplier from the Default Suppliers of the items below. On selection, a Purchase Order will be made against items belonging to the selected Supplier only.'),
				get_query: () => {
					return{
						query: "erpnext.stock.doctype.material_request.material_request.get_default_supplier_query",
						filters: {'doc': frm.doc.name}
					}
				}
			},
			(values) => {
        // Get the selected items from the Items table
        let selected_items = $.map(frm.fields_dict["items"].grid.get_selected_children(), function(d) {
          return d.name;
        });

        if (selected_items.length === 0) {
            frappe.msgprint(__('Please select items to include in the Request for Quotation.'));
            return;
        }

				frappe.model.open_mapped_doc({
					method: "erpnext.stock.doctype.material_request.material_request.make_purchase_order",
					frm: frm,
					args: { default_supplier: values.default_supplier , filtered_items: selected_items},
					run_link_triggers: true
				});
			},
			__('Enter Supplier'),
			__('Create')
		)
	},

	make_request_for_quotation: function(frm) {
    // Get the selected items from the Items table
    let selected_items = $.map(frm.fields_dict["items"].grid.get_selected_children(), function(d) {
      return d.name;
    });

    if (selected_items.length === 0) {
        frappe.msgprint(__('Please select items to include in the Request for Quotation.'));
        return;
    }

    // Call the server-side method to create the RFQ
    frappe.model.open_mapped_doc({
        method: "erpnext.stock.doctype.material_request.material_request.make_request_for_quotation",
        frm: frm,
        args: { filtered_items: selected_items },  // Pass selected item names
        run_link_triggers: true
    });
		
	},

	make_supplier_quotation: function(frm) {
    // Get the selected items from the Items table
    let selected_items = $.map(frm.fields_dict["items"].grid.get_selected_children(), function(d) {
      return d.name;
    });

    if (selected_items.length === 0) {
        frappe.msgprint(__('Please select items to include in the Request for Quotation.'));
        return;
    }

    // Call the server-side method to create the RFQ
    frappe.model.open_mapped_doc({
        method: "erpnext.stock.doctype.material_request.material_request.make_supplier_quotation",
        frm: frm,
        args: { filtered_items: selected_items },  // Pass selected item names
        run_link_triggers: true
    });
    
  },

  comparison : function (frm) {
    frm.events.setup_comparsion_query(frm)
    },
    get_filters: function(frm){
      if(frm.doc.comparison){
          frappe.call({
            method: "frappe.client.get",
            args: {
              doctype: "Comparison",
                name:frm.doc.comparison,
        },
        callback: function(r) {
                  if(r.message){
                      console.log(r.message.item);
                      let item = r.message.item ; 
                      const clearanceValues = item.map(item => item.clearance_item);;
                      console.log(clearanceValues);
                      frm.set_query('comparison_item', () => {
                          return {
                              filters: {
                                  name: ["in" , clearanceValues]
                              }
                          }
                      })
                  }

              }
          })
      }      

  },

    setup_comparsion_query:function(frm){
      if(frm.doc.comparison){
        frappe.call({
          "method" : "contracting_13.contracting_13.doctype.stock_functions.stock_entry_setup" ,
          args:{
            "comparison" : frm.doc.comparison,
          },
          freeze: true,
          async: true,
          callback :function(r){
            if (r.message){
              // console.log(r.message)
              // console.log(r.message.items)
              // frm.set_value("project",r.message.project)
              // frm.set_value("cost_center",r.message.cost_center)
              frm.set_query("comparison_item",function () {
                return {
                  filters: [
                    ["item_code", "in", r.message.items],
                  ],
                };
              });
              frm.refresh_field("comparison_item")
              frm.set_query("comparison_item","items",function () {
                return {
                  filters: [
                    ["item_code", "in", r.message.items],
                  ],
                };
              });
              frm.refresh_fields("items","cost_center","project")
            }
          } 
       
        })
      }
      
    },
    comparison_item:function(frm){
      if(frm.doc.comparison_item && frm.doc.comparison){
        frappe.call({
          "method" : "contracting_13.contracting_13.doctype.stock_functions.get_comparision_items" ,
          args:{
            "comparison" : frm.doc.comparison,
            "item_code" : frm.doc.comparison_item,
          },
          callback :function(r){
            if (r.message){
              frm.clear_table("items")
              $.each(r.message || [], function(i, element) {
                let row = frm.add_child('items', {
                  item_code: element.item_code,
                  item_name: element.item_name,
                  qty: element.total_qty,
                  uom: element.uom,
                  stock_uom: element.uom,
                  transfer_qty: element.total_qty * element.conversion_factor,
                  conversion_factor: element.conversion_factor,
                  basic_rate: element.unit_price,
                  cost_center: frm.doc.cost_center,
                  project: frm.doc.project,
                  item: frm.doc.comparison_item || "", 
                  
              });
              })
              frm.refresh_field("items")
            }
          } 
       
        })
      }
      
  
    },
    //[{'item_code': 'معدن مشكل', 'item_name': 'معدن مشكل', 'uom': None, 'qty': 100.0, 'unit_price': 1500.0, 'conversion_factor': 1}, {'item_code': 'اسمنت',
    // 'item_name': 'اسمنت', 'uom': None, 'qty': 20.0, 'unit_price': 250.0, 'conversion_factor': 1}]
    all_comparsion:function(frm){
      if(frm.doc.all_comparsion && frm.doc.comparison){
        frappe.call({
          "method" : "contracting_13.contracting_13.doctype.stock_functions.get_all_comparsion_item" ,
          args:{
            "comparsion" : frm.doc.comparison,
          },
          callback :function(r){
            if (r.message){
              frm.clear_table("items")
              $.each(r.message || [], function(i, element) {
                let row = frm.add_child('items', {
                  item_code: element.item_code,
                  item_name: element.item_name,
                  qty: element.total_qty * parseFloat(get_qty(frm.doc.comparison)),
                  uom: element.uom,
                  stock_uom: element.uom,
                  transfer_qty: element.total_qty * element.conversion_factor * parseFloat(get_qty(frm.doc.comparison)),
                  conversion_factor: element.conversion_factor,
                  basic_rate: element.unit_price,
                  project: element.project,
                  cost_center:element.cost_center,
                  item: element.item,
                  description: get_details(element.item_code)
                  
              });
              })
              frm.refresh_field("items")
            }
          } 
       
        })
      }
      
  
    },
    
    
})
function get_details(item_code){
  var description ; 
  frappe.call({
    async:false,
    method: "frappe.client.get",
    args: {
      doctype: "Item",
        name:item_code,
    },
    callback: function(r) {
              if(r.message){
                  description = r.message.description ; 
              }

          }
      })
      return description ; 
}

function get_qty(comparison){
  var table ; 
  frappe.call({
    async:false,
    method: "frappe.client.get",
    args: {
      doctype: "Comparison",
              name:comparison,
    },
    callback: function(r) {
              if(r.message){
                  let item = r.message.item ; 
                  const clearanceValues = item.map(item => item.qty)
                  table = clearanceValues[0] ;
              }

          }
      })
      return table ;
}
