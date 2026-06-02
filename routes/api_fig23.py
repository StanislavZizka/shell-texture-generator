"""Figure 2.3 route registration for the shared API blueprint."""

from __future__ import annotations

from routes.api import api, _generate_23_response


@api.route('/api/generate-23', methods=['POST'])
def generate_23():
    """Proxy Figure 2.3 requests to the shared response implementation."""
    return _generate_23_response()
