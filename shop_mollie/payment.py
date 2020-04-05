# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.utils.text import format_lazy
from django.utils.translation import ugettext_lazy as _
from django.conf.urls import url
from rest_framework.exceptions import ValidationError
from shop.models.order import OrderModel, OrderPayment
from shop.payment.providers import PaymentProvider
from mollie.api.client import Client
from mollie.api.error import Error
from shop.models.cart import CartModel
from uuid import uuid4
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import NoReverseMatch, resolve, reverse
from django.contrib.sites.shortcuts import get_current_site
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods



class MolliePayment(PaymentProvider):
    """
    Provides a payment service for Mollie.
    """
    namespace = 'mollie-payment'

    def get_urls(self):
        return [
            url(r'mollie-webhook/', csrf_exempt(self.mollie_webhook), name='mollie-webhook'), #webhook
        ]
    def build_absolute_url(self, request, endpoint):
        shop_ns = resolve(request.path).namespace
        url = reverse('{}:{}:{}'.format(shop_ns, self.namespace, endpoint))
        return request.build_absolute_uri(url)
        
    def create_payment_load(self, cart, request):
        """
        Create a payment ID with UUID4, what is sent to the PSP
        """
        mollie_client = Client()
        mollie_client.set_api_key(settings.SHOP_MOLLIE['MOLLIE_KEY'])
        cart = CartModel.objects.get_from_request(request)
        order = OrderModel.objects.create_from_cart(cart, request)
        order.populate_from_cart(cart, request)
        order.save(with_notification=False)
        payment_data =  {
            'amount': {
                'currency': 'EUR',
                'value': '%.2f' % cart.total
            },
            'description': 'Test payment', 
            'webhookUrl': self.build_absolute_url(request, 'mollie-webhook'),
            'redirectUrl': ''.join(['https://', settings.SHOP_MOLLIE['DOMAIN'], order.get_absolute_url()]),
            'metadata': {
                'order_id': order.get_number(),
            },
            'method': settings.SHOP_MOLLIE['MOLLIE_PAYMENT_METHODS'], #array of payment methods via Mollie
        }
        payment = mollie_client.payments.create(payment_data)
        return payment


    def get_payment_request(self, cart, request):
        """
        From the given request, redirect onto the checkout view, hosted by Mollie.
        """
        payment = self.create_payment_load(cart, request)
        redirect_url = payment.checkout_url
        return '$window.location.href="{0}";'.format(redirect_url)

    
    @classmethod
    def mollie_webhook(cls, request): #with unique identifier off the payment
        '''
        Mollie calls the webhook when the payment status changes.
        Here the call is commited to the Database.
        '''
        mollie_client = Client()
        mollie_client.set_api_key(settings.SHOP_MOLLIE['MOLLIE_KEY'])

        payment_id = request.POST['id']
        payment = mollie_client.payments.get(payment_id)
        order = OrderModel.objects.get(slug=payment.metadata['order_id']) 
        
        if payment.is_paid():
            order.add_mollie_payment(payment) # does this add the payment?
            order.extra['transaction_id'] = payment_id
            order.save(with_notification=True)
            return HttpResponse('Paid')
        elif payment.is_pending():
            #
            # The payment has started but is not complete yet. 
            #
            order.add_mollie_payment(payment) # does this add the payment?
            order.extra['transaction_id'] = payment_id
            order.save(with_notification=False)
            return HttpResponse('Pending')
        elif payment.is_open():
            #
            # The payment has not started yet. Wait for it.
            #
            order.add_mollie_payment(payment) # does this add the payment?
            order.extra['transaction_id'] = payment_id
            order.save(with_notification=False)
            return HttpResponse('Open')
        else:
            #
            # The payment isn't paid, pending nor open. We can assume it was aborted.
            # Cancel the order --> cancel view --> send mail
            #
            
            return HttpResponse('Cancelled') #we can redirect to a cancel page
