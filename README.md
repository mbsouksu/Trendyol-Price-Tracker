# Trendyol-Price-Tracker

If you put your `config.yaml` file in the same directory with the `tracker.py`, it will work one time and send mail(s) if there is a price that under tha target price and after sending the mail it will update the config file by deleting that link and price.

If you want to specify the path of the config file, you can use:

`python tracker.py -p [path]`

If you want to track until nothing to track, you can use:

`python tracker.py -i True`

