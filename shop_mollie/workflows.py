# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import ugettext_lazy as _
from django_fsm import transition
from shop.models.order import BaseOrder, OrderPayment
from shop.money import MoneyMaker
from shop_mollie.payment import MolliePayment


class MollieOrderWorkflowMixin(object):
    TRANSITION_TARGETS = {
        'paid_with_mollie': _("Paid with Mollie"),
    }

    def __init__(self, *args, **kwargs):
        if not isinstance(self, BaseOrder):
            raise ImproperlyConfigured("class 'OrderWorkflowMixin' is not of type 'BaseOrder'")

        super(MollieOrderWorkflowMixin, self).__init__(*args, **kwargs)

    @transition(field='status', source=['created'], target='paid_with_mollie')
    def add_mollie_payment(self, payment):
        assert self.currency == payment.amount['currency'], "Currency mismatch"
        Money = MoneyMaker(payment.amount['currency'])
        amount = Money(payment.amount['value'])
        OrderPayment.objects.create(
            order=self,
            amount=amount,
            transaction_id=payment['id'],
            payment_method=MolliePayment.namespace, #always ideal
        )

    def is_fully_paid(self):
        if super(MollieOrderWorkflowMixin, self).is_fully_paid():
            return True
        else:
            return False


    @transition(field='status', source='paid_with_mollie', conditions=[is_fully_paid],
                custom=dict(admin=True, button_name=_("Acknowledge Payment")))

    def acknowledge_mollie_payment(self):
        self.acknowledge_payment()
    
    def cancelable(self):
        return super(MollieOrderWorkflowMixin, self).cancelable() or self.status in ['paid_with_mollie']
'''
    def refund_payment(self):
        """
        Refund the payment using Stripe's refunding API.
        """
        Money = MoneyMaker(self.currency)
        filter_kwargs = {
            'transaction_id__startswith': 'ch_',
            'payment_method': StripePayment.namespace,
        }
        for payment in self.orderpayment_set.filter(**filter_kwargs):
            refund = stripe.Refund.create(charge=payment.transaction_id)
            if refund['status'] == 'succeeded':
                amount = Money(refund['amount']) / Money.subunits
                OrderPayment.objects.create(
                    order=self,
                    amount=-amount,
                    transaction_id=refund['id'],
                    payment_method=StripePayment.namespace,
                )

        del self.amount_paid  # to invalidate the cache
        if self.amount_paid:
            # proceed with other payment service providers
            super(MollieOrderWorkflowMixin, self).refund_payment()
'''
