import socket
from threading import Thread

import pyodbc

kullanicilar = {}
ipAdresleri = {}
groups = {}

SUNUCU = "127.0.0.1"
PORT = 18121
BUFFERSIZE = 1024
ADDR = (SUNUCU, PORT)
SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

SERVER.bind(ADDR)
cnxn_str = ("Driver={SQL Server Native Client 11.0};"
            "Server=DESKTOP-PGRQFNS;"
            "Database=chat;"
            "Trusted_Connection=yes;")
cnxn = pyodbc.connect(cnxn_str)
cursor = cnxn.cursor()

def gelenMesaj():
    while True:
        kullanici, kullanici_addresi = SERVER.accept()
        print("%s:%s Connected." % kullanici_addresi)
        kullanici.send(bytes("AgProgramlama ChatAPP Projesi" + " Nickname giriniz.", "utf8"))
        ipAdresleri[kullanici] = kullanici_addresi
        Thread(target=kullanici_Connected, args=(kullanici,)).start()


def kullanici_Connected(kullanici):
    nickname = kullanici.recv(BUFFERSIZE).decode("utf8")
    first_message = "Chat odasina %s! baglandi. Odadan ayrilmak icin disc yaziniz." % nickname
    kullanici.send(bytes(first_message, "utf8"))
    msg = "%s Chat kanalina baglandi!" % nickname
    mesaj_yayinla(bytes(msg, "utf8"))
    kullanicilar[kullanici] = nickname
    guncelle_kullanici_listesi()
    while True:
        try:
            msg = kullanici.recv(BUFFERSIZE)

            if msg.startswith(bytes("/msg", "utf8")):
                parts = msg.decode("utf8").split(" ", 2)
                if len(parts) >= 3:
                    target_user = parts[1]
                    messagePvr = parts[2]
                    for target_socket, kullanici_ad in kullanicilar.items():
                        if kullanici_ad == target_user:
                            target_socket.send(bytes("%s(DM):" % nickname, "utf8") + messagePvr.encode("utf8"))
                            break


            elif msg.startswith(bytes("/creategroup", "utf8")):
                parts = msg.decode("utf8").split(" ")
                if len(parts) >= 2:
                    group_name = parts[1]
                    group_members = parts[2:]
                    create_group(group_name, group_members)
                    mesaj_yayinla(
                        bytes(f"{group_name} adında bir grup oluşturuldu ve {', '.join(group_members)} üyeleri eklendi.",
                              "utf8"))
            elif msg.startswith(bytes("/groupmsg", "utf8")):
                parts = msg.decode("utf8").split(" ", 2)
                if len(parts) >= 3:
                    group_name = parts[1]
                    group_message = parts[2]
                    send_group_message(nickname, group_name, group_message)

            elif msg != bytes("disc", "utf8"):
                mesaj_yayinla(msg, nickname + ": ")
            else:
                kullanici.send(bytes("disc", "utf8"))
                kullanici.close()
                del kullanicilar[kullanici]
                guncelle_kullanici_listesi()
                cnxn.close()
                mesaj_yayinla(bytes("%s Sohbet odasindan cikis yapti." % nickname, "utf8"))
                break
        except ConnectionResetError:
            kullanici.close()
            del kullanicilar[kullanici]
            mesaj_yayinla(bytes("%s Sohbet odasindan cikis yapti." % nickname, "utf8"))
            guncelle_kullanici_listesi()
            break

def mesaj_yayinla(msg, kisi=""):
    cursor.execute("INSERT INTO messages (sender, message) VALUES (?, ?)", (kisi, msg.decode("utf8")))
    cnxn.commit()
    for msg_yayinla in kullanicilar:
        msg_yayinla.send(bytes(kisi, "utf8") + msg)



def guncelle_kullanici_listesi():
    kullanici_listesi = ",".join(kullanicilar.values())
    mesaj_yayinla(bytes("userlist", "utf8"))
    mesaj_yayinla(bytes(kullanici_listesi, "utf8"))


def create_group(group_name, members):
    groups[group_name] = members

def send_group_message(sender, group_name, message):
    if group_name in groups:
        members = groups[group_name]
        for client_socket, username in kullanicilar.items():
            if username in members:
                client_socket.send(bytes(f"(Grup) {sender}: {message}", "utf8"))

def grup_mesaji_yayinla(grup_adi, mesaj):
    for target_socket, kullanici_ad in kullanicilar.items():
        if kullanici_ad.startswith("Grup-") and kullanici_ad == grup_adi:
            target_socket.send(bytes("(Grup) ", "utf8") + mesaj.encode("utf8"))

if __name__ == "__main__":
    SERVER.listen(10)
    print("Baglanti bekleniyor...")
    THREAD_KABUL = Thread(target=gelenMesaj)
    THREAD_KABUL.start()
    THREAD_KABUL.join()
    SERVER.close()