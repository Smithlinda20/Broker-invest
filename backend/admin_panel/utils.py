from admin_panel.models import ActivityLog


def build_activity_log(
    user_or_profile,
    activity_type,
    description,
    amount=None,
    plan_name=None,
    status='pending',
    entity_id=None,
    metadata=None,
):
    if hasattr(user_or_profile, 'user'):
        user = user_or_profile.user
    else:
        user = user_or_profile

    return ActivityLog.objects.create(
        user_email=getattr(user, 'email', '') or '',
        username=getattr(user, 'username', '') or '',
        activity_type=activity_type,
        description=description,
        amount=amount,
        plan_name=plan_name,
        status=status,
        entity_id=str(entity_id) if entity_id else None,
        metadata=metadata or {},
    )


def activity_available_actions(activity):
    if activity.status != 'pending':
        return []

    if activity.activity_type in {'payment_pending', 'withdrawal_requested', 'wallet_import'}:
        return ['confirm', 'reject']

    return []
