import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
	columns = get_columns()
	data = get_data()
	return columns, data


def get_columns():
	return [
		{
			"label": _("Project"),
			"fieldname": "project",
			"fieldtype": "Link",
			"options": "Project",
			"width": 200,
		},
		{
			"label": _("Project Name"),
			"fieldname": "project_name",
			"fieldtype": "Data",
			"width": 220,
		},
		{
			"label": _("Customer"),
			"fieldname": "customer",
			"fieldtype": "Link",
			"options": "Customer",
			"width": 180,
		},
		{
			"label": _("Budgeted Hours"),
			"fieldname": "budgeted_hours",
			"fieldtype": "Float",
			"precision": 2,
			"width": 130,
		},
		{
			"label": _("Logged Hours"),
			"fieldname": "logged_hours",
			"fieldtype": "Float",
			"precision": 2,
			"width": 130,
		},
		{
			"label": _("Variance %"),
			"fieldname": "variance_pct",
			"fieldtype": "Percent",
			"width": 120,
		},
	]


def get_data():
	rows = frappe.db.sql(
		"""
		select
			name as project,
			project_name,
			customer,
			budgeted_hours,
			logged_hours
		from `tabProject`
		where ifnull(budgeted_hours, 0) > 0
		  and ifnull(logged_hours, 0) > ifnull(budgeted_hours, 0)
		order by (logged_hours - budgeted_hours) / budgeted_hours desc
		""",
		as_dict=True,
	)
	for row in rows:
		budgeted = flt(row.budgeted_hours)
		logged = flt(row.logged_hours)
		row["variance_pct"] = ((logged - budgeted) / budgeted) * 100.0 if budgeted else 0.0
	return rows
