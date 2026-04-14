// Copyright (c) 2026, Izge Turizm and contributors
// For license information, please see license.txt

frappe.ui.form.on('Aqua Importer', {
	refresh(frm) {
		// Visual status indicator
		if (frm.doc.status === 'Success') {
			frm.dashboard.set_headline(__('<span style="color:green;font-weight:bold;">✅ İmport başarılı!</span>'));
		} else if (frm.doc.status === 'Failed') {
			frm.dashboard.set_headline(__('<span style="color:red;font-weight:bold;">❌ İmport başarısız! Log detaylarını kontrol edin.</span>'));
		} else if (frm.doc.status === 'Partially Failed') {
			frm.dashboard.set_headline(__('<span style="color:orange;font-weight:bold;">⚠️ Kısmi başarı — bazı PNR\'ler aktarılamadı.</span>'));
		} else if (frm.doc.status === 'In Progress') {
			frm.dashboard.set_headline(__('<span style="color:blue;font-weight:bold;">⏳ İşleniyor...</span>'));
		}
	},

	process_button(frm) {
		if (frm.is_dirty()) {
			frappe.msgprint(__('Lütfen önce kaydedin.'));
			return;
		}
		if (!frm.doc.import_file) {
			frappe.msgprint(__('Lütfen önce bir dosya ekleyin.'));
			return;
		}

		frappe.confirm(
			__('Bu dosyayı işlemek istediğinize emin misiniz? Aynı PNR\'ye sahip mevcut Trip kayıtları güncellenecektir.'),
			function() {
				frm.set_df_property("process_button", "disabled", true);
				frappe.call({
					method: 'izge_travel.izge_travel.doctype.aqua_importer.aqua_importer.trigger_import',
					args: { docname: frm.doc.name },
					freeze: true,
					freeze_message: __('Import işleniyor... Bu biraz zaman alabilir.'),
					callback(r) {
						frm.reload_doc();
						if (!r.exc) {
							frappe.show_alert({
								message: __('Import işlemi tamamlandı. Detaylar için log bölümüne bakınız.'),
								indicator: 'green'
							});
						}
					}
				});
			}
		);
	}
});
