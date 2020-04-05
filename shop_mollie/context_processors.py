# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf import settings

def public_keys(request):
    return {
        'SHOP_MOLLIE_PUBKEY': settings.SHOP_STRIPE['PUBKEY'],
        'SHOP_MOLLIE_SECKEY': getattr(settings, 'SHOP_STRIPE_PREFILL', False)
    }