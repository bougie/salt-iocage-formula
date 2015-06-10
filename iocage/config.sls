{% set rawmap = salt['pillar.get']('iocage') %}

{% if rawmap.defaults is defined %}
    {% for property_name, property_value in rawmap.defaults.items() %}
iocage_{{property_name}}_default_property:
    iocage.property:
        - name: {{property_name}}
        - value: "{{property_value}}"
    {% endfor %}
{% endif %}

{% if rawmap.jails is defined %}
    {% for jail_name, properties in rawmap.jails.items() %}
        {% for property_name, property_value in properties.items() %}
iocage_{{property_name}}_{{jail_name}}_jail_property:
    iocage.property:
        - name: {{property_name}}
        - value: "{{property_value}}"
        - jail: {{jail_name}}
        {% endfor %}
    {% endfor %}
{% endif %}
