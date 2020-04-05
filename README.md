# djangoshop-mollie
Mollie Payment Provider Plug-in for Django-Shop version 1.0 and above

BE AWARE: this project is not tested properly

## Installation

for django-shop version 1.0.x:

```
pip install djangoshop-mollie<1.1 (not available yet)
```

## Configuration

In ``settings.py`` of the merchant's project:

Add ``'shop_mollie'`` to ``INSTALLED_APPS``.

At [Mollie](https://mollie.com/) create an account and register your shop. 
For a testing account add them as:

```
SHOP_MOLLIE = {
    'MOLLIE_KEY': '<test-key-provided-by-Mollie>',
    'PURCHASE_DESCRIPTION': "Thanks for purchasing at My Shop",
    'MOLLIE_PAYMENT_METHODS': ['ideal', 'applepay']
}
```

and for production:

```
SHOP_MOLLIE = {
    'MOLLIE_KEY': '<live-key-provided-by-Mollie>',
    'PURCHASE_DESCRIPTION': "Thanks for purchasing at My Shop",
    'MOLLIE_PAYMENT_METHODS': ['ideal', 'applepay']
}
```
Change the payment methods to the methods activated in the Mollie dashboard

Add ``'shop_mollie.modifiers.MolliePaymentModifier'`` to the list of ``SHOP_CART_MODIFIERS``.

Add ``'shop_mollie.workflows.MollieOrderWorkflowMixin'`` to the list of ``SHOP_ORDER_WORKFLOWS``.

When rendering the payment method form, "Mollie" shall appear in the list of possible payments.

Successful payments are redirected onto the just created order detail page.

There is no handling for cancellation of payment yet

## Changes

none