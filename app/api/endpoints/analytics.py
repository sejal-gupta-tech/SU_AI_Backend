"""
Analytics API endpoint.

GET /api/v1/analytics/overview?range=7d|30d|90d

Returns a comprehensive analytics overview for the authenticated user,
sourced entirely from real MongoDB data.  External metrics return null
because the required social integrations are not implemented.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.database import get_database
from app.core.security import get_current_user
from app.services.analytics_service import AnalyticsService, VALID_RANGES

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/overview")
async def get_analytics_overview(
    date_range: str = Query(
        "30d",
        alias="range",
        description="Date range filter: 7d, 30d, or 90d",
    ),
    current_user=Depends(get_current_user),
):
    """
    Authenticated analytics overview.

    Supported ranges: ``7d``, ``30d``, ``90d``.
    Invalid values return HTTP 400.

    All data comes from real MongoDB records scoped to the
    authenticated user.  Empty collections and missing businesses
    return valid zero/null responses — the API never crashes.
    """
    # ── Validate range ───────────────────────────────────────────────
    if date_range not in VALID_RANGES:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Invalid range '{date_range}'. "
                f"Must be one of: {', '.join(sorted(VALID_RANGES.keys()))}"
            ),
        )

    # ── Build analytics ──────────────────────────────────────────────
    try:
        db = get_database()
        service = AnalyticsService(db)
        # CurrentUser is a dict subclass — both .get() and attribute access are safe
        user_id = str(current_user.get("id") or current_user.id)
        business_id = current_user.get("business_id")
        result = await service.get_overview(
            user_id=user_id,
            business_id=business_id,
            range_param=date_range,
        )
        return {"success": True, "data": result}
    except HTTPException:
        raise  # Re-raise known HTTP errors
    except Exception as exc:
        logger.error(
            "Analytics overview failed for user %s: %s",
            current_user.id,
            exc,
            exc_info=True,
        )
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve analytics. Please try again later.",
        )
