class KNNNode:
    def __init__(self, **kwargs):
        for field in ('node_id', 'longitude', 'latitude', 'distance'):
            setattr(self, field, kwargs.get(field, None))
