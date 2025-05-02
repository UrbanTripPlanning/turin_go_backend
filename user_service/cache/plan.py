from user_service.cache import base


AFFECTED_PLAN_KEY = 'affected_plan'


def set_affected_plans(plans):
    for plan in plans:
        key = f'{AFFECTED_PLAN_KEY}:{plan["user_id"]}:{plan["plan_id"]}'
        base.set_cache(key, plan, plan['ts'])


def get_affected_plans(user_id: str):
    list_key = f'{AFFECTED_PLAN_KEY}:{user_id}'
    return base.list_cache(list_key)


def remove_affected_plan_if_needed(plan_id: str):
    list_key = f'{AFFECTED_PLAN_KEY}:'
    all_plans = base.list_cache(list_key)
    for plan in all_plans:
        if plan['plan_id'] == plan_id:
            key = f'{AFFECTED_PLAN_KEY}:{plan["user_id"]}:{plan["plan_id"]}'
            base.delete_cache(key)
            break
