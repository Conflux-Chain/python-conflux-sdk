cfx_utils.token_unit
=============

A module providing methods to operate token units in Conflux.

Currently :class:`cfx_utils.token_unit.Drip`, :class:`cfx_utils.token_unit.CFX` and :class:`cfx_utils.token_unit.GDrip`
can be imported from :mod:`cfx_utils.token_unit`. These classes inherits from `cfx_utils.token_unit.AbstractTokenUnit` and
support computing or comparing::

    >>> from cfx_utils.token_unit import CFX, Drip
    >>> CFX(1)
    1 CFX
    >>> CFX(1).value
    1
    >>> Drip(1)
    1 Drip
    >>> CFX(1) == Drip(1) * 10**18
    True
    >>> Drip(1) * 2
    2 Drip
    >>> CFX(1) / Drip(1)
    Decimal('1000000000000000000')
    >>> Drip(1) / 2
    Traceback (most recent call last):
        ...
    cfx_utils.exceptions.InvalidTokenOperation: ...

.. autoclass:: cfx_utils.token_unit.Drip
    :members:
    :undoc-members:
    :inherited-members:
    :private-members: _decimals, _base_unit

.. autoclass:: cfx_utils.token_unit.CFX
    :members:
    :undoc-members:
    :inherited-members:
    :private-members: _decimals, _base_unit

.. autoclass:: cfx_utils.token_unit.AbstractTokenUnit
    :members:
    :special-members:
    :member-order: bysource
    :exclude-members: __weakref__

.. automethod:: cfx_utils.token_unit.to_int_if_drip_units
