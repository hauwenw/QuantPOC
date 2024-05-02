# Quant POC

### Installation (Mac)

```commandline
brew install ta-lib
pip install -r requirements.txt
```

### Usage
```commandline
python main.py --stock_id 0050.tw --period 1y --strategy SmaCross
```

The result plot will show in pop-up browser. Detail stats will show in logs.

Note: The value for `--strategy` is class name under `strategies` module
