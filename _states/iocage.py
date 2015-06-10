# -*- coding: utf-8 -*-
'''
Support for iocage (jails tools on FreeBSD)
'''
from __future__ import absolute_import


def _property(name, value, jail, **kwargs):
    ret = {'name': name,
           'changes': {},
           'comment': '',
           'result': False}

    try:
        old_value = __salt__['iocage.get_property'](name, jail, **kwargs)

        if jail == 'defaults':
            jail = 'default'
    except:
        if __opts__['test']:
            ret['result'] = None
            if jail == 'default':
                ret['comment'] = 'default option %s seems do not exist' % (
                    name,)
            else:
                ret['comment'] = 'jail option %s seems do not exist' % (name,)
        else:
            ret['result'] = False
            if jail == 'default':
                ret['comment'] = 'default option %s does not exist' % (name,)
            else:
                ret['comment'] = 'jail option %s does not exist' % (name,)
    else:
        if value != old_value:
            ret['changes'] = {'new': value, 'old': old_value}

            if not __opts__['test']:
                try:
                    __salt__['iocage.set_property'](jail, **{name: value})
                except:
                    ret['result'] = False
                else:
                    ret['result'] = True
            else:
                ret['result'] = None
        else:
            if __opts__['test']:
                ret['result'] = None
            else:
                ret['result'] = True

    return ret


def property(name, value, jail=None, **kwargs):
    if jail is None:
        return _property(name, value, 'defaults', **kwargs)
    else:
        return _property(name, value, jail, **kwargs)


if __name__ == "__main__":
    __salt__ = ''
    __opts__ = ''

    import sys
    sys.exit(0)
