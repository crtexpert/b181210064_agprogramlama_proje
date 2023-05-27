from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import tkinter


def gonder(event=None):
    msg = message.get()
    message.set("")
    kullanici_socket.send(msg.encode("utf8"))
    if msg == "disc":
        kullanici_socket.close()
        app.quit()


def guncelle_kullanici_listesi(kullanici_listesi):
    userList.delete(0, tkinter.END)
    kullanici_listesi = kullanici_listesi.split(",")
    for kullanici in kullanici_listesi:
        userList.insert(tkinter.END, kullanici)


def gelen_mesaj():
    while True:
        try:
            msg = kullanici_socket.recv(BUFFERSIZE)
            if msg.decode("utf8").startswith("userlist"):
                kullanici_listesi = kullanici_socket.recv(BUFFERSIZE).decode("utf8")
                guncelle_kullanici_listesi(kullanici_listesi)
            else:
                messageList.insert(tkinter.END, msg.decode("utf8"))
        except:
            break


def cikis(event=None):
    message.set("disc")
    gonder()


def grup_mesaji_gonder(event=None):
    secilen_kullanicilar = userList.curselection()
    if secilen_kullanicilar:
        grup_adi = "Grup-" + kullanici_socket.getsockname()[0]
        mesaj = "(Grup) " + message.get()
        kullanici_socket.send(bytes("/groupmsg %s %s" % (grup_adi, mesaj), "utf8"))



app = tkinter.Tk()
app.title("AgProgramlama ChatApp")

messageBox = tkinter.Frame(app)
message = tkinter.StringVar()
message.set("Mesaj giriniz..")
scrollbar = tkinter.Scrollbar(messageBox)
userList = tkinter.Listbox(app, height=20, width=20, selectmode=tkinter.MULTIPLE)
messageList = tkinter.Listbox(messageBox, height=20, width=70, yscrollcommand=scrollbar.set)
messageList.see("end")
scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
messageList.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
userList.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
messageBox.pack()
giris_alani = tkinter.Entry(app, textvariable=message)
giris_alani.bind("<Return>", gonder)
giris_alani.pack()
gonderButton = tkinter.Button(app, text="Gonder", command=gonder)
gonderButton.pack()

SUNUCU = '127.0.0.1'
PORT = 18121
BUFFERSIZE = 1024
ADDR = (SUNUCU, PORT)
kullanici_socket = socket(AF_INET, SOCK_STREAM)
kullanici_socket.connect(ADDR)
username = kullanici_socket.getsockname()[0]


if not PORT:
    PORT = 18121
else:
    PORT = int(PORT)



gelen_thread = Thread(target=gelen_mesaj)
gelen_thread.start()
tkinter.mainloop()