from __future__ import annotations
from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from tunnels import Tunnel

subscriptions = {}

def add_subscription(subscription: Tunnel):
    uuid = subscription.v.uuid
    provider = subscription.provider_name
    url = subscription.url

    if uuid not in subscriptions:
        subscriptions[uuid] = {}
    if subscription.public_url:
        subscriptions[uuid][provider] = url

def remove_subscription(subscription: Tunnel):
    uuid = subscription.v.uuid
    provider = subscription.provider_name

    if uuid in subscriptions and provider in subscriptions[uuid]:
        del subscriptions[uuid][provider]
        if not subscriptions[uuid]:
            del subscriptions[uuid]
    


