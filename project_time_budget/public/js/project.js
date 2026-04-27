frappe.ui.form.on("Project", {
	refresh(frm) {
		render_budget_indicator(frm);
	},
	budgeted_hours(frm) {
		render_budget_indicator(frm);
	},
	logged_hours(frm) {
		render_budget_indicator(frm);
	},
});

function render_budget_indicator(frm) {
	const budgeted = flt(frm.doc.budgeted_hours);
	const logged = flt(frm.doc.logged_hours);

	if (!budgeted) {
		frm.dashboard.clear_headline();
		return;
	}

	const pct = (logged / budgeted) * 100;
	let color = "green";
	if (pct > 100) {
		color = "red";
	} else if (pct >= 80) {
		color = "orange";
	}

	const message = __("Time budget: {0} / {1} hours ({2}%)", [
		format_number(logged, null, 2),
		format_number(budgeted, null, 2),
		format_number(pct, null, 1),
	]);
	frm.dashboard.set_headline_alert(message, color);
}
