# app/routes/analytics.py
"""
Analytics routes for TalentGrid Dashboard.
Provides real-time statistics from the database.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from pydantic import BaseModel

from app.database import get_db
from app.models.user import User
from app.models.candidate import Candidate
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


class StatItem(BaseModel):
    label: str
    value: str
    change: str
    changeType: str
    description: str


class ActivityItem(BaseModel):
    action: str
    time: str
    type: str


class DashboardStats(BaseModel):
    stats: List[StatItem]
    recentActivity: List[ActivityItem]
    totalCandidates: int
    newThisWeek: int
    avgMatchScore: int


@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get dashboard statistics from real database data.
    """
    # Calculate real stats
    total_candidates = db.query(Candidate).count()

    # Candidates added in the last 7 days
    week_ago = datetime.now(timezone.utc) - timedelta(days=7)
    new_this_week = db.query(Candidate).filter(
        Candidate.created_at >= week_ago
    ).count()

    # Candidates added in the last 30 days (for comparison)
    month_ago = datetime.now(timezone.utc) - timedelta(days=30)
    new_this_month = db.query(Candidate).filter(
        Candidate.created_at >= month_ago
    ).count()

    # Calculate average match score (if available)
    avg_match = db.query(func.avg(Candidate.match_percentage)).scalar() or 0
    avg_match = int(avg_match)

    # Calculate week-over-week change
    two_weeks_ago = datetime.now(timezone.utc) - timedelta(days=14)
    prev_week_count = db.query(Candidate).filter(
        Candidate.created_at >= two_weeks_ago,
        Candidate.created_at < week_ago
    ).count()

    if prev_week_count > 0:
        week_change = int(((new_this_week - prev_week_count) / prev_week_count) * 100)
    else:
        week_change = 100 if new_this_week > 0 else 0

    # Build stats array
    stats = [
        StatItem(
            label='Total Candidates',
            value=str(total_candidates),
            change=f'+{new_this_month}' if new_this_month > 0 else '0',
            changeType='positive' if new_this_month > 0 else 'neutral',
            description='this month'
        ),
        StatItem(
            label='New This Week',
            value=str(new_this_week),
            change=f'+{week_change}%' if week_change >= 0 else f'{week_change}%',
            changeType='positive' if week_change >= 0 else 'negative',
            description='vs last week'
        ),
        StatItem(
            label='Avg Match Score',
            value=f'{avg_match}%' if avg_match > 0 else 'N/A',
            change='+0%',
            changeType='neutral',
            description='across all candidates'
        ),
        StatItem(
            label='Database Status',
            value='Active',
            change='Online',
            changeType='positive',
            description='all systems operational'
        ),
    ]

    # Get recent candidates for activity feed
    recent_candidates = db.query(Candidate).order_by(
        Candidate.created_at.desc()
    ).limit(5).all()

    recent_activity = []
    for candidate in recent_candidates:
        time_diff = datetime.now(timezone.utc) - (candidate.created_at or datetime.now(timezone.utc))
        if time_diff.days > 0:
            time_str = f'{time_diff.days} day{"s" if time_diff.days > 1 else ""} ago'
        elif time_diff.seconds >= 3600:
            hours = time_diff.seconds // 3600
            time_str = f'{hours} hour{"s" if hours > 1 else ""} ago'
        else:
            minutes = time_diff.seconds // 60
            time_str = f'{minutes} minute{"s" if minutes > 1 else ""} ago'

        recent_activity.append(ActivityItem(
            action=f'CV imported: {candidate.name}',
            time=time_str,
            type='import'
        ))

    # Add placeholder if no recent activity
    if not recent_activity:
        recent_activity.append(ActivityItem(
            action='No recent activity. Import some CVs to get started!',
            time='Just now',
            type='info'
        ))

    return DashboardStats(
        stats=stats,
        recentActivity=recent_activity,
        totalCandidates=total_candidates,
        newThisWeek=new_this_week,
        avgMatchScore=avg_match
    )


@router.get("/candidates/by-source")
async def get_candidates_by_source(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get candidate count grouped by source."""
    results = db.query(
        Candidate.source,
        func.count(Candidate.id).label('count')
    ).group_by(Candidate.source).all()

    return {
        "data": [{"source": r.source or "unknown", "count": r.count} for r in results]
    }


@router.get("/candidates/by-status")
async def get_candidates_by_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get candidate count grouped by status."""
    results = db.query(
        Candidate.status,
        func.count(Candidate.id).label('count')
    ).group_by(Candidate.status).all()

    return {
        "data": [{"status": r.status or "new", "count": r.count} for r in results]
    }
