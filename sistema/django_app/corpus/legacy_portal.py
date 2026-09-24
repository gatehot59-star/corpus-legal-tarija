"""Compatibility endpoints for the original lawyer-only employee portal."""
from .employee_portal import portal_delete, portal_reissue


def portal_reissue_lawyer(request, account_id):
    """Route the former password endpoint to the lawyer account handler."""
    return portal_reissue(request, "lawyer", account_id)


def portal_delete_lawyer(request, account_id):
    """Route the former delete endpoint to the lawyer account handler."""
    return portal_delete(request, "lawyer", account_id)
