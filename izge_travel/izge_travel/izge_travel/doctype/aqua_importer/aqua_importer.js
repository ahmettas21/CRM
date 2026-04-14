frappe.ui.form.on('Aqua Importer', {
	process_button: function(frm) {
		if (frm.is_dirty()) {
			frappe.msgprint(__('Please save the document before processing.'));
			return;
		}
		if (!frm.doc.import_file) {
			frappe.msgprint(__('Please attach a file before processing.'));
			return;
		}
		
		frappe.confirm(__('Are you sure you want to process this file? Existing trips with same PNRs will be overwritten.'),
			function() {
				frm.set_df_property("process_button", "disabled", true);
				frappe.call({
					method: 'izge_travel.izge_travel.doctype.aqua_importer.aqua_importer.trigger_import',
					args: {
						docname: frm.doc.name
					},
					freeze: true,
					freeze_message: __('Processing Import... This might take a while.'),
					callback: function(r) {
						frm.reload_doc();
						if(!r.exc) {
							frappe.show_alert({message: __('Import processing completed.'), indicator: 'green'});
						}
					}
				});
			}
		);
	}
});
