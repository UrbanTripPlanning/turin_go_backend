from user_service.cache import base


AFFECTED_PLAN_KEY = 'affected_plan'


def set_affected_plans(plans):
    for plan in plans:
        key = f'{AFFECTED_PLAN_KEY}:{plan["user_id"]}:{plan["plan_id"]}'
        base.set_cache(key, plan, plan['ts'])


def get_affected_plans(user_id: str):
    list_key = f'{AFFECTED_PLAN_KEY}:{user_id}'
    return base.list_cache(list_key)
