from collections import defaultdict
from sanic.response import json
from sanic import Blueprint

from connections import get_client

alias_bp = Blueprint('alias')


def format_alias_addition(action):
    data = {
        "index": action['index'],
        "alias": action['alias']
    }
    if action.get("filter") != {} and action.get("filter") not in {"", None}:
        data["filter"] = action["filter"]
    if action.get("searchRouting") not in {"", None}:
        data["search_routing"] = action["searchRouting"]
    if action.get("indexRouting") not in {"", None}:
        data["index_routing"] = action["indexRouting"]

    return {action['action']: data}


async def get_index_aliases():
    client = get_client()
    aliases = await client.cat.aliases(format='json')
    aliases_by_index = defaultdict(list)
    for alias in aliases:
        aliases_by_index[alias['index']].append(alias['alias'])
    return dict([(x, sorted(aliases_by_index[x])) for x in aliases_by_index])


@alias_bp.route('/batch', methods=['POST'])
async def create_alias(request):
    client = get_client()
    actions = request.json['actions']
    print({"actions": [format_alias_addition(action) for action in actions]})
    await client.indices.update_aliases(
        {"actions": [format_alias_addition(action) for action in actions]}
    )
    return json({"status": "ok"})