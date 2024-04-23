frappe.ui.form.on("Material Request",{

  onload:function(frm) {
    frm.events.get_filters(frm)
  },
  setup:function(frm){
    frm.events.setup_comparsion_query(frm)
  },

  refresh:function(frm){
    frm.events.setup_comparsion_query(frm)
    
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
