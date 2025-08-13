queries
===========


Description
-----------

Contains various functions to query the building data.


Functions
---------

To find closest buildings use ``queries.assign_closest_lookup[MappedObject: Base](SearchTable: type[MappedObject], LookupTable: type[MappedObject], session: Session) -> list[tuple[MappedObject, MappedObject]]:``.

.. autofunction:: queries.assign_closest_lookup

The ``validator`` should be a function that accepts a *string* and returns *(bool, str)*