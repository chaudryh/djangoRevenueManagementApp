

if __name__ == '__main__':
    import os
    import sys

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sys.path.append(BASE_DIR)

    from Celery.RollOver.tasks import *

    roll_over_retail_bowling.delay()
    roll_over_retail_shoe.delay()
    roll_over_product.delay()