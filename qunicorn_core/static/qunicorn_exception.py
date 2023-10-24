class QunicornError(Exception):
    """General Exception raised for errors in qunicorn"""

    def __init__(self, msg, status_code=404):
        super().__init__(msg)
        self.status_code = status_code
