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


def managed(name, properties=None, **kwargs):
    ret = {'name': name,
           'changes': {},
           'comment': '',
           'result': False}

    # test if a jail already exists
    # if it does not exist, a create command will be launch
    try:
        jail_exists = False

        jails = __salt__['iocage.list_jails']().split('\n')
        for jail in jails:
            jail_datas = {j.split('=')[0]: '='.join(j.split('=')[1:])
                          for j in jail.split(',')}
            if jail_datas['TAG'] == name or jail_datas['UUID'] == name:
                jail_exists = True
                break
    except:
        if __opts__['test']:
            ret['result'] = None
        ret['comment'] = 'unable to check if jail exists or not'

        return ret

    try:
        # get jail's properties if exists or defaults
        if jail_exists:
            _name = name
        else:
            _name = 'defaults'
        jail_properties = __salt__['iocage.list_properties'](_name, **kwargs)
    except:
        jail_properties = None
    finally:
        if (jail_properties is not None
                and properties is not None
                and len(properties) > 0):
            jail_properties = {prop.split('=')[0]: '='.join(prop.split('=')[1:])
                               for prop in jail_properties.split('\n')}
            if jail_exists:
                # set new value for each property
                try:
                    changes = {}
                    for prop_name, prop_value in properties.items():
                        if prop_name in jail_properties.keys():
                            if prop_value != jail_properties[prop_name]:
                                changes[prop_name] = {
                                    'new': prop_value,
                                    'old': jail_properties[prop_name]}

                                __salt__['iocage.set_property'](
                                    name,
                                    **{prop_name: prop_value})
                    if len(changes) > 0:
                        ret['changes'] = changes
                        ret['comment'] = 'updating %s\'s jail properties' % (
                            name,)
                    else:
                        ret['comment'] = 'no change have to be done'
                except:
                    ret['result'] = False
                else:
                    if __opts__['test']:
                        ret['result'] = None
                    else:
                        ret['result'] = True
            else:
                # install / create the jail
                try:
                    if not __opts__['test']:
                        if properties is not None:
                            __salt__['iocage.create'](tag=name, **properties)
                        else:
                            __salt__['iocage.create'](tag=name, **kwargs)
                except:
                    ret['result'] = False
                    ret['comment'] = 'fail installing new jail %s' % (name,)
                else:
                    if __opts__['test']:
                        ret['result'] = None
                    else:
                        ret['result'] = True
                    ret['comment'] = 'New jail %s installed' % (name,)

    return ret


if __name__ == "__main__":
    __salt__ = ''
    __opts__ = ''

    import sys
    sys.exit(0)
