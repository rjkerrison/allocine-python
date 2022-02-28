def dumper(obj):
    try:
        return obj.toJSON()
    except Exception as f:
        print('Exception for toJSON', f, type(obj))
        return obj.__dict__
