#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
meandra.datastore
=================

Centralizes input/output operations and data handling in pipelines.

The `datastore` module is responsible for managing interactions with data throughout the pipeline
lifecycle. It implements mechanisms for dynamic path resolution, resource discovery, loading and
saving (reading/writing) in multiple formats. It introduces data providers as a unified layer
between framework components and underlying data sources, coupled with a data catalog system to
automate data access on request.


Modules
-------


See Also
--------
test_datastore
    Tests for the datastore module.
"""
