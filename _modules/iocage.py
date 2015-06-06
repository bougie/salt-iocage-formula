# -*- coding: utf-8 -*-
'''
Support for iocage (jails tooks on FreeBSD)
'''
from __future__ import absolute_import

# Import python libs
# import os

import logging
# Import salt libs
import salt.utils
from salt.exceptions import CommandExecutionError, SaltInvocationError

log = logging.getLogger(__name__)

__virtualname__ = 'iocage'


def __virtual__():
    '''
    Module load only if php is installed
    '''
    if salt.utils.which('iocage'):
        return __virtualname__
    else:
        return False


def _option_exists(name, **kwargs):
    '''
    Check if a given property is in the all properties list
    '''
    return name in list_properties(name, **kwargs)


def _exec(cmd, output='stdout'):
    cmd_ret = __salt__['cmd.run_all'](cmd)
    if cmd_ret['retcode'] == 0:
        return cmd_ret[output]
    else:
        raise CommandExecutionError(
            'Error in command "%s" : %s' % (cmd, str(cmd_ret)))


def _list_properties(jail_name, **kwargs):
    '''
    Returns result of iocage get all or iocage defaults (according to the
    jail name)
    '''
    if jail_name == 'defaults':
        cmd = 'iocage defaults'
    else:
        cmd = 'iocage get all %s' % (jail_name,)

    return _exec(cmd).split('\n')


def _parse_properties(**kwargs):
    default_properties = [p.split('=')[0] for p in _list_properties('defaults')]

    for prop in kwargs.keys():
        if not prop.startswith('__') and prop not in default_properties:
            raise SaltInvocationError('Unknown property %s' % (prop,))

    return ' '.join(
        ['%s=%s' % (k, v) for k, v in kwargs.items() if not k.startswith('__')])


def _list(option=None, **kwargs):
    '''
    Returns list of jails, templates or releases
    '''
    if option not in [None, '-t', '-r']:
        raise SaltInvocationError('Bad option name in command _list')

    cmd = 'iocage list'
    if option == '-t' or option == '-r':
        cmd = '%s %s' % (cmd, option)
    lines = _exec(cmd, **kwargs).split('\n')

    if len(lines) > 0:
        if option == '-r':
            headers = ['RELEASE']
        else:
            headers = [_ for _ in lines[0].split(' ') if len(_) > 0]

        jails = []
        if len(lines) > 1:
            for l in lines[1:]:
                jails.append({
                    headers[k]: v for k, v in enumerate([_ for _ in l.split(' ')
                                                         if len(_) > 0])
                })

        return jails
    else:
        raise CommandExecutionError(
            'Error in command "%s" : no results found' % (cmd, ))


def _display_list(items_list):
    '''
    Format display for the list of jails, templates or releases
    '''
    ret = ''

    for item in items_list:
        ret += '%s\n' % (','.join(['%s=%s' % (k, v) for k, v in item.items()]),)

    return ret


def _manage_state(state, jail_name, **kwargs):
    '''
    Start / Stop / Reboot / Destroy a jail
    '''
    existing_jails = _list()
    for jail in existing_jails:
        if jail_name == jail['UUID'] or jail_name == jail['TAG']:
            if ((state == 'start' and jail['STATE'] == 'down')
                    or (state == 'stop' and jail['STATE'] == 'up')
                    or state == 'restart'
                    or state == 'destroy'):
                return _exec('iocage %s %s' % (state, jail_name))
            else:
                if state == 'start':
                    raise SaltInvocationError(
                        'jail %s is already started' % (jail_name,))
                else:
                    raise SaltInvocationError(
                        'jail %s is already stoped' % (jail_name,))

    raise SaltInvocationError('jail uuid or tag does not exist' % (jail_name,))


def list_jails(**kwargs):
    '''
    Get list of jails

    CLI Example:

    .. code-block:: bash

        salt '*' iocage.list_jails
    '''
    return _display_list(_list())


def list_templates(**kwargs):
    '''
    Get list of template jails

    CLI Example:

    .. code-block:: bash

        salt '*' iocage.list_templates
    '''
    return _display_list(_list('-t'))


def list_releases(**kwargs):
    '''
    Get list of downloaded releases

    CLI Example:

    .. code-block:: bash

        salt '*' iocage.list_releases
    '''
    return _display_list(_list('-r'))


def list_properties(jail_name, **kwargs):
    '''
    List all properies for a given jail or defaults value

    CLI Example:

    .. code-block:: bash

        salt '*' iocage.list_properties <jail_name>
        salt '*' iocage.list_properties defaults
    '''
    props = _list_properties(jail_name, **kwargs)

    # hack to have the same output with defaults or for a given jail
    if jail_name == 'defaults':
        return '\n'.join(props)
    else:
        return '\n'.join([_.replace(':', '=', 1) for _ in props])


def get_property(property_name, jail_name, **kwargs):
    '''
    Get property value for a given jail (or default value)

    CLI Example:

    .. code-block:: bash

        salt '*' iocage.get_property <property> <jail_name>
        salt '*' iocage.get_property <property> defaults
    '''
    if property_name == 'all':
        return list_properties(jail_name, **kwargs)
    else:
        return _exec('iocage get %s %s' % (property_name, jail_name))


def create(option=None, **kwargs):
    '''
    Create a new jail

    CLI Example:

    .. code-block:: bash

        salt '*' iocage.create [<option>] [<property=value>]
    '''
    _options = [None, 'clone', 'base']

    if option not in _options:
        raise SaltInvocationError('Unknown option %s' % (option,))

    # stringify the kwargs dict into iocage create properties format
    properties = _parse_properties(**kwargs)

    # if we would like to specify a tag value for the jail
    # check if another jail have not the same tag
    if 'tag' in kwargs.keys():
        existing_jails = _list()
        if kwargs['tag'] in [k['TAG'] for k in existing_jails]:
            raise SaltInvocationError(
                'Tag %s already exists' % (kwargs['tag'],))

    if option is not None and len(properties) > 0:
        cmd = 'iocage create %s %s' % (option, properties)
    else:
        cmd = 'iocage create %s' % (properties,)
    return _exec(cmd)


def start(jail_name, **kwargs):
    '''
    Start a jail

    CLI Example:

    .. code-block:: bash

        salt '*' iocage.start <jail_name>
    '''
    return _manage_state('start', jail_name, **kwargs)


def stop(jail_name, **kwargs):
    '''
    Stop a jail

    CLI Example:

    .. code-block:: bash

        salt '*' iocage.stop <jail_name>
    '''
    return _manage_state('stop', jail_name, **kwargs)


def restart(jail_name, **kwargs):
    '''
    Restart a jail

    CLI Example:

    .. code-block:: bash

        salt '*' iocage.restart <jail_name>
    '''
    return _manage_state('restart', jail_name, **kwargs)


def destroy(jail_name, **kwargs):
    '''
    Destroy a jail

    CLI Example:

    .. code-block:: bash

        salt '*' iocage.destroy <jail_name>
    '''
    return _manage_state('destroy', jail_name, **kwargs)


if __name__ == "__main__":
    __salt__ = ''

    import sys
    sys.exit(0)
