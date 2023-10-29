## Step 8

This step will introduce test suite.

### Test suite

Quite often the directory which contains tests is named `tests` (naturaly).

There are several suites for tests. In this case the `pytest` is used.
We need python packages.
To distinc runtime and development setup it is possible to define
`requirements-dev.txt` file.

It is possible to reinstall all packages from `requirements-dev.txt` file with

```
pip install -r requirements-dev.txt --force
```

the `--force` parameter ensures that all packages will be reinstaled.

To run tests there is command

```
pytest --cov-report term-missing --cov=DBDefinitions --cov=GraphTypeDefinitions --cov=utils
```


### SQLite

To be able run tests without database backend we could use SQLite.
A problem with uuid loads from file appears.
To avoid them string values should be converted into uuid value.
This can be done in `utils.DBFeeder.py` file.
Look for 
```python
            if "id" in key:
                json_dict[key] = uuid.UUID(value)
```

### Tests

Many tests need smae initialization.
Such utils are placed in `tests.shared.py` file.
There are

- `prepare_in_memory_sqllite`, init sqlite server
- `prepare_demodata`, fullfil in memory data
- `createContext`, creates a datastructure for GQL schema execution

There are also generalized tests.
The generalization has been made by closures implementation.
In this case there are functions which create tests.
In file `tests.test_gt_definitions.py` are

- `createByIdTest`, create, run and evaluate a query type `eventById`
- `createPageTest`, create, run and evaluate a query type `eventPage`
- `createResolveReferenceTest`, create, run and evaluate a query type `_entities` (low level system query)
- `createFrontendQuery`, allows to define any query with variables and test result with list of lambdas

Some tests are complex and beyond tools above.
As an example there is `test_event_update`.

If the tests are executed

```
pytest --cov-report term-missing --cov=DBDefinitions --cov=GraphTypeDefinitions --cov=utils
```

Result shoud look like

```
tests\test_dbdefinitions.py ....                                                                                                                                                                 [ 36%]
tests\test_gt_definitions.py .......                                                                                                                                                             [100%]

---------- coverage: platform win32, python 3.10.10-final-0 ----------
Name                                    Stmts   Miss  Cover   Missing
---------------------------------------------------------------------
DBDefinitions\__init__.py                  31      4    87%   23-26
DBDefinitions\baseDBModel.py                3      0   100%
DBDefinitions\eventDBModel.py              14      0   100%
DBDefinitions\uuid.py                       2      0   100%
GraphTypeDefinitions\__init__.py           15      1    93%   12
GraphTypeDefinitions\eventGQLModel.py      86      1    99%   16
utils\DBFeeder.py                          36      5    86%   20, 25-27, 45
utils\Dataloaders.py                       72     16    78%   19, 54-71
---------------------------------------------------------------------
TOTAL                                     259     27    90%
```

There are not covered source lines. They are bounded by `await` expressions.
This can be fixed by addition of file `.coveragearc` with content

```
[run]
concurrency = gevent
```

`gevent` is package which must be installed.

Now the coverage report shows

```
---------- coverage: platform win32, python 3.10.10-final-0 ----------
Name                                    Stmts   Miss  Cover   Missing
---------------------------------------------------------------------
DBDefinitions\__init__.py                  31      4    87%   23-26
DBDefinitions\baseDBModel.py                3      0   100%
DBDefinitions\eventDBModel.py              14      0   100%
DBDefinitions\uuid.py                       2      0   100%
GraphTypeDefinitions\__init__.py           15      1    93%   12
GraphTypeDefinitions\eventGQLModel.py      86      1    99%   16
utils\DBFeeder.py                          36      5    86%   20, 25-27, 45
utils\Dataloaders.py                       72      2    97%   19, 58
---------------------------------------------------------------------
TOTAL                                     259     13    95%
```

### conclusion

Tests are important part of reliable software.
For python based software pytest can be used.
It is also important to cover as much as possible source code lines.
For such check there is possible to get coverage report.

In this project tests are available with command

```
pytest --cov-report term-missing --cov=DBDefinitions --cov=GraphTypeDefinitions --cov=utils
```

The source code is not covered at 100%.

Also take into account that some errors in previous steps have been found and corrected thanks to tests.