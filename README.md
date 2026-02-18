# Termsg

**Termsg** es un sistema de chat seguro por terminal escrito en Python, que utiliza **TLS con autenticación mutua (mTLS)** para comunicaciones cifradas entre clientes y servidor.

Está pensado como:
- Proyecto educativo
- Chat ligero por terminal
- Laboratorio de redes, TLS y sockets
- Base para extender a más funcionalidades

---

## 🚀 Características

- 🔐 Comunicación cifrada con TLS
- 🧾 Autenticación por certificados (cliente y servidor)
- 🧵 Soporte para múltiples clientes simultáneos
- 🖥️ Interfaz por terminal
- 📡 Compatible con Wireshark (tráfico TLS)
- 🧼 Sin colores ANSI (compatible con Windows, Linux y macOS)

---

## 📦 Requisitos

- ![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)
- ![OpenSSL](https://img.shields.io/badge/OpenSSL-orange.svg)
- ![Windows](https://img.shields.io/badge/Windows-blue.svg) ![Linux](https://img.shields.io/badge/Linux-Yellow.svg) ![MacOS](https://img.shields.io/badge/MacOS-grey.svg)

---

## 🔑 Certificados (TLS con mTLS)

Termsg utiliza **TLS con autenticación mutua**, lo que significa:

- El servidor verifica a los clientes
- Los clientes verifican al servidor
- Solo usuarios con certificado válido pueden conectarse

### Autoridad certificadora (CA)

El archivo `ca.cnf` define la CA local usada para firmar los certificados

Para generar los certificados usaremos:
```
openssl genrsa -out [tu_nombre].key 2048
openssl req -new -key [tu_nombre].key -out [tu_nombre].csr -subj "/C=ES/ST=[CIUDAD]/L=[Localidad]/O=ChatTerm/OU=ChatTermUnit/CN=[tu_nombre]"
openssl x509 -req -in [tu_nombre].csr -CA ca.crt -CAkey ca.key -CAcreateserial -out [tu_nombre].crt -days 365
```
Si capturas con un sniffer esto es lo que se ve:

![image](https://github.com/nestoree/termsg/blob/main/images/snif_cert.png)

---

## 🖥️ Uso

Iniciar el servidor
```
python3 server.py <nombre_de_la_sala>
```

Conectar un cliente
```
python3 client.py <IP_del_servidor> <nombre.crt> <nombre.key>
```

---

## 💬 Comandos disponibles

| Comando     | Descripción                 |
| ----------- | --------------------------- |
| `/usuarios` | Muestra usuarios conectados |
| `/clear`    | Limpia la pantalla          |
| `/quit`     | Salir del chat              |

---

## ⚠️ Seguridad

Este proyecto NO está pensado para producción sin mejoras adicionales:

- No hay control de revocación (CRL / OCSP)
- No hay persistencia de usuarios
- No hay protección contra DoS

Está orientado a aprendizaje y experimentación.

---

## 📜 Licencia

MIT License
