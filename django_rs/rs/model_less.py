class KnnNode:
    def __init__(self, **kwargs):
        for field in ('node', 'longitude', 'latitude', 'distance'):
            setattr(self, field, kwargs.get(field, None))
