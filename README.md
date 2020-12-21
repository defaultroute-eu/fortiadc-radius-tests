# FortiADC UDP Load Balancing Test Cases


## Requirements

At least Python 3.8

## Setup


    # Create venv
    python -mvenv .venv
    . .venv/bin/activate
    pip install -r requirements.txt


## Testing

    # python test_fortiadc.py --vip 1.2.3.4 --rserver 5.6.7.8 --shared-secret '<radius_shared_secret>' --username '<username>' --password '<password>'
    send to:     5.6.7.8:1812     reply from:    5.6.7.8:1812
    send to:     1.2.3.4:1812     reply from:    1.2.3.4:1812
    send to:     5.6.7.8:1812     reply from:    1.2.3.4:1812


Send to addresses and reply from should match
