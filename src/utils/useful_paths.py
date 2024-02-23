from pathlib import Path

CFPQ_PYALGO_ROOT = Path(__file__).parent.parent.parent

GLOBAL_CFPQ_DATA = Path(CFPQ_PYALGO_ROOT).joinpath('deps/CFPQ_Data/data')
LOCAL_CFPQ_DATA = Path(CFPQ_PYALGO_ROOT).joinpath('test/data')
POCR_FORMAT_DATA = Path(CFPQ_PYALGO_ROOT).joinpath('test/pocr_data')
