# -*- coding: utf-8 -*-
"""NNC OSER — reusable control plane for Claude Code project repositories.

The plugin owns the framework (this package, catalogs, templates). Each project owns its effective
configuration under `.claude/oser/project.json`; everything OSER writes into a project is either a
marked GENERATED artifact recorded in `.claude/oser/lock.json`, or a one-time scaffold the project
then owns.
"""
