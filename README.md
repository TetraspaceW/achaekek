# achaekek

Manifold markets Python API

Create a new Manifold client 

```python
from achaekek import Client
client = Client(api_key="YOUR API KEY")
```

Make requests via this client

```python
new_market = CreateMultipleChoiceMarket(
        question="Will creating this test market work?",
        answers=["Yes", "No"],
    )
client.create_market(new_market)
```

Enjoy your market! 