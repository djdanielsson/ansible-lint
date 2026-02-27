# set-fact-in-loop

This rule flags use of `ansible.builtin.set_fact` inside a loop, which
is a performance anti-pattern.

When `set_fact` is used inside a loop, Ansible re-evaluates the entire
fact on every iteration. For large lists, this causes quadratic time
complexity and significant slowdowns. The most common pattern is
building a list by appending to it in each iteration:

```yaml
# Slow - O(n^2) behavior
- name: Build list
  ansible.builtin.set_fact:
    my_list: "{{ my_list | default([]) + [item] }}"
  loop: "{{ large_list }}"
```

Instead, use Jinja2 filters like `map`, `select`, `selectattr`, or
`json_query` to transform data in a single expression.

This is an opt-in rule.
You must enable it in your Ansible-lint configuration as follows:

```yaml
enable_list:
  - set-fact-in-loop
```

## Problematic Code

```yaml
---
- name: Example playbook
  hosts: all
  tasks:
    - name: Build list of names
      ansible.builtin.set_fact:
        name_list: "{{ name_list | default([]) + [item.name] }}" # <- Slow.
      loop: "{{ users }}"

    - name: Build list with with_items
      ansible.builtin.set_fact:
        name_list: "{{ name_list | default([]) + [item.name] }}" # <- Also slow.
      with_items: "{{ users }}"
```

## Correct Code

```yaml
---
- name: Example playbook
  hosts: all
  tasks:
    - name: Build list of names
      ansible.builtin.set_fact:
        name_list: "{{ users | map(attribute='name') | list }}" # <- Fast.

    - name: Set a simple fact
      ansible.builtin.set_fact:
        app_version: "1.0.0" # <- No loop, no problem.
```
