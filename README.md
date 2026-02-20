# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/pretalx/pretalx-venueless/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                               |    Stmts |     Miss |   Branch |   BrPart |   Cover |   Missing |
|----------------------------------- | -------: | -------: | -------: | -------: | ------: | --------: |
| pretalx\_venueless/\_\_init\_\_.py |        1 |        0 |        0 |        0 |    100% |           |
| pretalx\_venueless/apps.py         |       15 |        0 |        0 |        0 |    100% |           |
| pretalx\_venueless/forms.py        |       35 |        1 |       14 |        1 |     96% |        37 |
| pretalx\_venueless/models.py       |       20 |        0 |        0 |        0 |    100% |           |
| pretalx\_venueless/signals.py      |       38 |        4 |        6 |        1 |     89% | 56, 70-75 |
| pretalx\_venueless/venueless.py    |       11 |        0 |        2 |        0 |    100% |           |
| pretalx\_venueless/views.py        |       86 |       16 |       22 |        4 |     78% |70->72, 73, 84, 98-132 |
| **TOTAL**                          |  **206** |   **21** |   **44** |    **6** | **88%** |           |


## Setup coverage badge

Below are examples of the badges you can use in your main branch `README` file.

### Direct image

[![Coverage badge](https://raw.githubusercontent.com/pretalx/pretalx-venueless/python-coverage-comment-action-data/badge.svg)](https://htmlpreview.github.io/?https://github.com/pretalx/pretalx-venueless/blob/python-coverage-comment-action-data/htmlcov/index.html)

This is the one to use if your repository is private or if you don't want to customize anything.

### [Shields.io](https://shields.io) Json Endpoint

[![Coverage badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/pretalx/pretalx-venueless/python-coverage-comment-action-data/endpoint.json)](https://htmlpreview.github.io/?https://github.com/pretalx/pretalx-venueless/blob/python-coverage-comment-action-data/htmlcov/index.html)

Using this one will allow you to [customize](https://shields.io/endpoint) the look of your badge.
It won't work with private repositories. It won't be refreshed more than once per five minutes.

### [Shields.io](https://shields.io) Dynamic Badge

[![Coverage badge](https://img.shields.io/badge/dynamic/json?color=brightgreen&label=coverage&query=%24.message&url=https%3A%2F%2Fraw.githubusercontent.com%2Fpretalx%2Fpretalx-venueless%2Fpython-coverage-comment-action-data%2Fendpoint.json)](https://htmlpreview.github.io/?https://github.com/pretalx/pretalx-venueless/blob/python-coverage-comment-action-data/htmlcov/index.html)

This one will always be the same color. It won't work for private repos. I'm not even sure why we included it.

## What is that?

This branch is part of the
[python-coverage-comment-action](https://github.com/marketplace/actions/python-coverage-comment)
GitHub Action. All the files in this branch are automatically generated and may be
overwritten at any moment.