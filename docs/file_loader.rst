file_loader
===========


Description
-----------

Contains various function for selecting *csv-files* and validate them.


Functions
---------

To select a *csv-file* with specific requirements you can use the ``file_loader.load_files()`` function.

.. autofunction:: file_loader.load_files

The ``validator`` should be a function that accepts a *string* and returns *(bool, str)*