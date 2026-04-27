import frappe
from frappe.model.document import Document


class TimeBudgetSettings(Document):
	pass


def get_hard_limit_percentage() -> float:
	value = frappe.db.get_single_value("Time Budget Settings", "hard_limit_percentage")
	if value in (None, 0):
		return 120.0
	return float(value)
