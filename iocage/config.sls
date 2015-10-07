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
iocage_{{jail_name}}_jail:
    iocage.managed:
        - name: {{jail_name}}
        {% if 'properties' in properties.keys() %}
            {% for option_name, option_value in properties.items() %}
                {% if option_name != 'properties' %}
        - {{option_name}}: "{{option_value}}"
                {% endif %}
            {% endfor %}
        - properties:
            {% for property_name, property_value in properties.properties.items() %}
            {{property_name}}: "{{property_value}}"
            {% endfor %}
        {% else %}
        - properties:
            {% for property_name, property_value in properties.items() %}
            {{property_name}}: "{{property_value}}"
            {% endfor %}
        {% endif %}
    {% endfor %}
{% endif %}
