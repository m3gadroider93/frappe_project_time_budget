import frappe
from frappe import _
from frappe.utils import flt

from project_time_budget.project_time_budget.doctype.time_budget_settings.time_budget_settings import (
	get_hard_limit_percentage,
)


def logged_hours_for_project(project: str) -> float:
	"""Sum hours from submitted Timesheet Detail rows for the given project."""
	result = frappe.db.sql(
		"""
		select coalesce(sum(td.hours), 0)
		from `tabTimesheet Detail` td
		inner join `tabTimesheet` ts on ts.name = td.parent
		where td.project = %s and ts.docstatus = 1
		""",
		(project,),
	)
	return flt(result[0][0]) if result else 0.0


def recalculate_project(project: str) -> float:
	total = logged_hours_for_project(project)
	frappe.db.set_value(
		"Project",
		project,
		"logged_hours",
		total,
		update_modified=False,
	)
	return total


def projects_in_timesheet(doc) -> list[str]:
	seen: list[str] = []
	for row in doc.get("time_logs") or []:
		project = row.get("project") if isinstance(row, dict) else getattr(row, "project", None)
		if project and project not in seen:
			seen.append(project)
	return seen


def recalculate_from_timesheet(doc, method=None):
	for project in projects_in_timesheet(doc):
		recalculate_project(project)


def validate_hard_limit(doc, method=None):
	"""Block submission if any project's projected logged hours would exceed the hard limit."""
	limit_pct = get_hard_limit_percentage()

	# Aggregate hours this timesheet adds per project.
	added: dict[str, float] = {}
	for row in doc.get("time_logs") or []:
		project = row.get("project") if isinstance(row, dict) else getattr(row, "project", None)
		hours = row.get("hours") if isinstance(row, dict) else getattr(row, "hours", None)
		if not project:
			continue
		added[project] = added.get(project, 0.0) + flt(hours)

	for project, extra_hours in added.items():
		project_row = frappe.db.get_value(
			"Project",
			project,
			["budgeted_hours", "logged_hours", "project_name"],
			as_dict=True,
		)
		if not project_row:
			continue
		budgeted = flt(project_row.budgeted_hours)
		if budgeted <= 0:
			# No budget set => nothing to enforce.
			continue
		projected = flt(project_row.logged_hours) + flt(extra_hours)
		limit_hours = budgeted * limit_pct / 100.0
		if projected > limit_hours:
			projected_pct = (projected / budgeted) * 100.0
			frappe.throw(
				_(
					"Submitting this Timesheet would push project <b>{0}</b> to "
					"{1} hours ({2}% of the {3} hour budget), which exceeds the "
					"hard limit of {4}%."
				).format(
					project_row.project_name or project,
					f"{projected:.2f}",
					f"{projected_pct:.1f}",
					f"{budgeted:.2f}",
					f"{limit_pct:.1f}",
				),
				title=_("Project Time Budget Exceeded"),
			)
