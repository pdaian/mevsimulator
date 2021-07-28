def prettyprint(obj):
    attributes = [(attr, obj.__dict__.get(attr, None)) for attr in dir(obj) if not attr.startswith('__')]
    print(attributes)
