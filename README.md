# Comandos uteis

1. Faz um backup dos dados a aplicação no arquivo 0001_DevData.json:
```python -Xutf8 manage.py dumpdata core --indent 4 -o core/seed/0001_DevData.json```

<br>

2. Faz a restauração dos dados apartir do arquivo "0001_DevData.json"
```python -Xutf8 manage.py loaddata core/seed/0001_DevData.json ```