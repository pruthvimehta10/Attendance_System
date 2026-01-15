#!/usr/bin/env python
import os
from app import create_app

app = create_app()
app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
