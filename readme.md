# Python Chat Application

## O aplikacji

Prosty komunikator typu messenger służący do komunikacji. Wykonany korzystając z protokołów TCP/UDP i działający na zasadzie klient-serwer.

Możliwości komunikatora to:

* wysyłanie wiadomości tekstowych (korzystając z protokołu TCP)
* wysyłanie obrazów (JPG, JPEG, PNG) o rozmiarze max. 64KB (korzystając z protokołu UDP)
* wysyłanie obrazów (JPG, JPEG, PNG) o rozmiarze max. 64KB multicastem (korzystając z protokołu UDP)

## Technologie

* Python 3.9
* PyQt5
* Pillow - obsługa obrazów



## Jak uruchomić?

1. W pierwszej kolejności należy uruchomić skrypt serwera korzystając z polecenia:

   ```shell
   $ python ./server.py
   ```

2. Gdy serwer jest już uruchomiony należy uruchomić pojedynczego klienta korzystając z polecenia:

   ```bash
   $ python ./main.py
   ```

   