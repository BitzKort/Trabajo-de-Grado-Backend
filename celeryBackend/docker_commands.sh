# start_celery.sh
#!/bin/bash


# 10:57 pm te das cuenta que docker solo es de un proceso principal :)
# me refiero, seria posible pero no con un sh, seria mesclarlos en una sola instruccion pero no tendria un orden
# Iniciar worker en segundo plano
celery -A task.celery_app worker --loglevel=info --logfile=worker.log --concurrency=3 --pool=prefork &

# Iniciar beat en segundo plano
celery -A task.celery_app beat --loglevel=info --logfile=beat.log &

# Iniciar Flower en primer plano (para mantener el contenedor activo)
celery -A task.celery_app flower --port=5555 --logfile=flower.log