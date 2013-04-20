# encoding: utf-8

"""
    froshki.ext.trafaret_attr
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    Implements froshki.Attribute extension with
    trafaret<https://github.com/Deepwalker/trafaret> data validation library.

    :copyright: (c) 2013 by ymat<drowse314@gmail.com>.
    :license: BSD, see LICENSE for more details.
"""

try:
    import trafaret
except ImportError:
    raise ImportError('trafaret is not installed')
from froshki import Attribute


class TrafaretPoweredAttribute(Attribute):
    """
    froshki.Attribute subclass using trafaret validation
    system.

    classmethod validate(klass, input_value) is used for handling
    trafaret validation, which is to be non-overridable.
    """

    trafaret = trafaret.Any()

    @classmethod
    def validate(klass, input_value):
        try:
            checked = klass.trafaret.check(input_value)
            return True, checked
        except trafaret.DataError as err:
            return False, err.error


def trafaret_attr(trafaret, name='TrafaretAttribute'):
    """
    trafaret_attr(trafaret) -> TrafaretPoweredAttribute subclass.

    TrafaretPoweredAttribute subclass factory.
    Usage:
    >>> import trafaret
    >>> from froshki import Froshki, validation_hook
    >>> class SendInquiry(Froshki):
    ...     user_name = trafaret_attr(trafaret.String())()
    ...     user_contact = trafaret_attr(trafaret.Email())()
    ...     user_contact_confirmation = trafaret_attr(trafaret.Email())()
    ...     message = trafaret_attr(trafaret.String(regex=r'\w{,400}'))()
    ...     @validation_hook
    ...     def confirm_email(self):
    ...         return self.user_contact == self.user_contact_confirmation
    >>>
    >>> send_inquiry = SendInquiry(user_name='yu mat', user_contact='drowse314@gmail.com', user_contact_confirmation='drowse314@gmail.com', message='cannot post messages to my group')
    >>> send_inquiry.validate()
    True
    """
    return type(
        name, (TrafaretPoweredAttribute,),
        dict(
            trafaret=trafaret,
        ),
    )
