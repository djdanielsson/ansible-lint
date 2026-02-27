# type-cast-variables

This rule flags numeric comparisons in `when` conditions where the
variable is not cast with `| int` or `| float`.

Ansible variables sourced from facts, user input, or inventory are often
strings. When a string is compared to a number using operators like `>`,
`<`, `>=`, or `<=`, Python performs a string comparison instead of a
numeric one, leading to unexpected results. For example, the string
`"9"` is greater than `"80"` in a string comparison because `"9"` comes
after `"8"` lexicographically.

Always use `| int` or `| float` filters to ensure the variable is cast
to the correct type before performing numeric comparisons.

This is an opt-in rule.
You must enable it in your Ansible-lint configuration as follows:

```yaml
enable_list:
  - type-cast-variables
```

## Problematic Code

```yaml
---
- name: Example playbook
  hosts: all
  tasks:
    - name: Check OS version
      ansible.builtin.debug:
        msg: "New enough"
      when: ansible_distribution_major_version >= 8 # <- String vs int comparison.

    - name: Check port range
      ansible.builtin.debug:
        msg: "Valid port"
      when: custom_port > 1024 # <- May fail if custom_port is a string.
```

## Correct Code

```yaml
---
- name: Example playbook
  hosts: all
  tasks:
    - name: Check OS version
      ansible.builtin.debug:
        msg: "New enough"
      when: ansible_distribution_major_version | int >= 8 # <- Explicit cast.

    - name: Check port range
      ansible.builtin.debug:
        msg: "Valid port"
      when: custom_port | int > 1024 # <- Safe numeric comparison.

    - name: Check threshold
      ansible.builtin.debug:
        msg: "Within limit"
      when: usage_percent | float <= 95.5 # <- Float cast for decimals.
```
