# WatchPower API in Python

By using Jadx and decompiling the WatchPower Android APK, I reverse-engineered its authentication process to have direct access to the backend's Rest-API. This way, we can programmatically query inverter data. I've made this available through a Python package in pip:

```shell
pip install watchpower-api
```

Check the examples folder for how to use the library.
To run examples or develop for this library its best to use [Poetry](https://python-poetry.org/). Clone the project and run:

```
poetry install
```

It should install all necessary dependencies.
