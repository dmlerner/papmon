import datetime

def debug(*args, **kwargs):
    # TODO: use built in logging library
    #return
    #print(*args, **kwargs, file=debug.file)
    print('>>>', *args, **kwargs)

# TODO: mkdir utils with time.py? 
def get_time(t):
    return t if type(t) is datetime.time else t.time()

def on_today(t):
    return datetime.datetime.combine(
            datetime.date.today(),
            get_time(t))

def now_time():
    return now_datetime().time()

def now_datetime():
    return datetime.datetime.now()

def nowish(t, margin_s=10):
    assert type(t) in (datetime.datetime, datetime.time)
    if type(t) is datetime.datetime:
        now = now_datetime()
    else: 
        now = now_time()
    return abs(t - now) < datetime.timedelta(seconds=margin_s)

ONE_DAY = datetime.timedelta(days=1)
