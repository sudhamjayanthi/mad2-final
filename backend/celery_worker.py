from main import app
from tasks import make_celery

celery = make_celery(app)
