# iocage

Install iocage and install FreeBSD jails with it.

**note**

See the full [Salt Formulas installation and usage instructions](http://docs.saltstack.com/en/latest/topics/development/conventions/formulas.html).

## Usage

Manage freebsd jails:
- fetch a release
- create a jail
- start / stop / restart / destroy a jail
- list jails / release / templates
- list / get / set jail properties

The main keys are **name**, **properties**, **jail_type** and **template_id**.

```yaml
iocage_test_jail:
    iocage.managed:
        - name: test_jail
        - properties:
            ip4_addr:lo1|10.1.1.20/32
        # optional default is full
        - jail_type: full
        # required only if jail_type is template-clone
        - template_id: ""
```

- **name** : the name property is the tag that is used to create the jail. This is a required field.
- **properties** : a list of key value pairs. All properties listed in `iocage defaults` can be set here. Also the pkglist property can be set here.
- **jail_type** : the type of jail to create.. Can be one of full , clone (-c), base (-b), template-clone, empty (-e). To create a template jail, just set 'template=yes' in properties. Default is full
- **template_id** : if the jail jail_type is template clone, then the template to be cloned is defined here. This is required if the jail_type is set to template_clone

## Examples

### Full Jail

Create a full jail with default properties:
```yaml
iocage_test_jail:
    iocage.managed:
        - name: test_jail
```

Create a full jail with some properties set:
```yaml
iocage_test_jail:
    iocage.managed:
        - name: test_jail
        - properties:
            ip4_addr: lo1|10.1.1.20/32
```

### Cloned Jail

Create a cloned jail:
```yaml
iocage_test_jail:
    iocage.managed:
        - name: test_jail
        - jail_type: clone
        - properties:
            ip4_addr: lo1|10.1.1.20/32
```

### Template Jail

Create a template jail:
```yaml
iocage_test_jail:
    iocage.managed:
        - name: test_jail
        - properties:
            ip4_addr: lo1|10.1.1.20/32
        # note the quotes for yes. Without it yaml parses it as true
        - template: "yes"
```

Clone a template. This will clone the template with tag test_template
```yaml
iocage_test_jail:
    iocage.managed:
        - name: test_jail
        - jail_type: template-clone
        - template_id: test_template
        - properties:
            ip4_addr: lo1|10.1.1.20/32
```
