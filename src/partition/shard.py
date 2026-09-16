import torch
from collections import OrderedDict

def get_layer_prefixes(state_dict):
    prefixes = []
    seen = set()
    for key in state_dict.keys():
        prefix = key.split('.')[0]
        if prefix not in seen:
            seen.add(prefix)
            prefixes.append(prefix)
    return prefixes

def partition(state_dict, n_shards):
    prefixes = get_layer_prefixes(state_dict)
    size = len(prefixes) // n_shards
    groups = []
    for i in range(n_shards):
        start = i * size
        end = start + size if i < n_shards - 1 else len(prefixes)
        groups.append(prefixes[start:end])

    shards = []
    for group in groups:
        shard = OrderedDict()
        for key, val in state_dict.items():
            if key.split('.')[0] in group:
                shard[key] = val
        shards.append(shard)
    return shards

def substitute(repaired_sd, infected_sd, shard_idx, n_shards):
    infected_shards = partition(infected_sd, n_shards)
    target_shard = infected_shards[shard_idx]

    new_sd = OrderedDict(repaired_sd)
    for key, val in target_shard.items():
        new_sd[key] = val
    return new_sd