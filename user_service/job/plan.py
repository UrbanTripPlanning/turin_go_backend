import httpx
from user_service.cache import plan as plan_cache
from utils.load import ROUTING_SERVICE_URL, DATA_SERVICE_URL


async def check_future_plans():
    async with httpx.AsyncClient() as client:
        resp = await client.get(f'{DATA_SERVICE_URL}/plan/list/all')
    plan_list = resp.json()
    affected_plans = []

    for old_plan in plan_list:
        old_time_duration = old_plan['spend_time']
        req = {
            'start_at': old_plan['start_at'],
            'end_at': old_plan['end_at'],
            'src_loc': old_plan['src_loc'],
            'dst_loc': old_plan['dst_loc'],
        }

        async with httpx.AsyncClient() as client:
            resp = await client.get(f'{ROUTING_SERVICE_URL}/route/search', params=req)
        new_plan = resp.json()
        if old_plan['route_mode'] == 0:
            new_time_duration = new_plan['walking']['times']
        else:
            new_time_duration = new_plan['driving']['times']

        if abs(new_time_duration-old_time_duration) <= 1:
            continue
        old_plan['spend_time'] = new_time_duration
        old_plan['ts'] = max(int(old_plan['start_at']) + int(old_plan['spend_time'])*60, int(old_plan['end_at']))
        affected_plans.append(old_plan)
    plan_cache.set_affected_plans(affected_plans)
