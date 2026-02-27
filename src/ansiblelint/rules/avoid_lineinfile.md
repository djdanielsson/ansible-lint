# avoid-lineinfile

This rule flags use of `ansible.builtin.lineinfile`, suggesting
`ansible.builtin.template` as a more maintainable alternative.

While `lineinfile` is convenient for quick one-line changes, it has
several drawbacks for configuration management:

- **Fragility**: Regex patterns can break when the file format changes.
- **Partial view**: Reviewers only see individual lines, not the full
  file structure, making it harder to understand the final result.
- **Maintenance burden**: Multiple `lineinfile` tasks for the same file
  are harder to maintain than a single template.
- **Idempotency risks**: Complex `regexp` patterns may match unintended
  lines or fail to match after upstream changes.

Using `ansible.builtin.template` provides a complete view of the target
file and makes changes easier to review, test, and maintain.

This is an opt-in rule.
You must enable it in your Ansible-lint configuration as follows:

```yaml
enable_list:
  - avoid-lineinfile
```

## Problematic Code

```yaml
---
- name: Example playbook
  hosts: all
  tasks:
    - name: Set application port
      ansible.builtin.lineinfile:
        path: /etc/myapp/app.conf
        regexp: "^PORT=" # <- Fragile regex pattern.
        line: "PORT=8080"

    - name: Set application host
      ansible.builtin.lineinfile:
        path: /etc/myapp/app.conf
        regexp: "^HOST=" # <- Another lineinfile for the same file.
        line: "HOST=0.0.0.0"
```

## Correct Code

```yaml
---
- name: Example playbook
  hosts: all
  tasks:
    - name: Deploy application config
      ansible.builtin.template:
        src: app.conf.j2 # <- Full file view, easy to review.
        dest: /etc/myapp/app.conf
        mode: "0644"
```

Where `app.conf.j2` contains:

```jinja
PORT={{ app_port }}
HOST={{ app_host }}
```
