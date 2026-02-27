# template-instead-of-copy

This rule flags use of `ansible.builtin.copy` for configuration files,
suggesting `ansible.builtin.template` as a more maintainable alternative.

Configuration files deployed with `copy` cannot leverage Jinja2 variables.
Even if a file is currently static, using `template` from the start makes
it trivial to add variables later without refactoring. Templates also
provide a clearer view of the full file structure during code review.

The rule triggers when the `dest` path is under `/etc/` or ends with a
known configuration file extension (`.conf`, `.cfg`, `.ini`, `.yml`,
`.yaml`, `.json`, `.xml`, `.properties`, `.toml`, `.env`).

This is an opt-in rule.
You must enable it in your Ansible-lint configuration as follows:

```yaml
enable_list:
  - template-instead-of-copy
```

## Problematic Code

```yaml
---
- name: Example playbook
  hosts: all
  tasks:
    - name: Deploy application config
      ansible.builtin.copy:
        src: app.conf # <- Static copy of a config file.
        dest: /etc/myapp/app.conf
        mode: "0644"

    - name: Deploy settings
      ansible.builtin.copy:
        src: settings.yml # <- Hard to add variables later.
        dest: /opt/app/settings.yml
        mode: "0644"
```

## Correct Code

```yaml
---
- name: Example playbook
  hosts: all
  tasks:
    - name: Deploy application config
      ansible.builtin.template:
        src: app.conf.j2 # <- Easy to add variables when needed.
        dest: /etc/myapp/app.conf
        mode: "0644"

    - name: Deploy settings
      ansible.builtin.template:
        src: settings.yml.j2 # <- Maintainable from the start.
        dest: /opt/app/settings.yml
        mode: "0644"

    - name: Copy a binary archive
      ansible.builtin.copy:
        src: app.tar.gz # <- Not a config file, copy is fine.
        dest: /opt/app/app.tar.gz
        mode: "0644"
```
