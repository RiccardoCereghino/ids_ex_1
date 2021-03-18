IDS exercise 1 documentation
=========================================
.. automodule:: indicator.functional
    :members:

.. raw:: latex

    \newpage

.. code-block:: python

    def csv_reader(file_name: str) -> Iterator[str]:
        for line in open(file_name, "r", encoding="utf8"):
            yield line

.. code-block:: python

    def row_splitter(row: str) -> List[str]:
        return row[:-1].split(',')
