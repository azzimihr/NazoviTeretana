import hashlib, os, math

from Ui import *

def start():
    global persons, acc
    persons = load(Person)
    login()
    return acc

def encrypt(string):
    return hashlib.sha256(string.encode('utf-8')).hexdigest()

def login(name='', pasw=''):
    global persons, acc
    logwin = win("Prijava", 250, 335)
    acc = ''
    pad= Frame(logwin, 'top', expand=False, pad=[0,15])
    un = box("Korisničko ime:", pad, name, fcs=True)
    pw = box("Lozinka:", pad, pasw, pw=True)
    
    def process(guest=False):
        global acc
        if guest:
            result = msg(logwin,
            """Koristićete nalog gosta tokom ove sesije.\nRazne opcije će biti ograničene. Nastaviti?""", yn=1)
            if result:
                acc="Gost"
                logwin.destroy()
        elif not un.get() in persons:
            msg(logwin, "Korisnik nije nađen.")
        elif persons[un.get()].deleted:
            msg(logwin, "Korisnik je izbrisan.")
        elif persons[un.get()].pw != encrypt(pw.get()+persons[un.get()].salt):
            msg(logwin, "Netačna lozinka.")
        else:
            acc=un.get()
            logwin.destroy()
			
    Button(logwin, "ULOGUJ SE    >", process, 'Accent')
    Button(logwin, "REGISTRACIJA", lambda: (
        logwin.destroy(), 
		register(un.get(), pw.get())))
    Button(logwin, "REŽIM GOSTA ", lambda: process(True),)
    
    logwin.bind('<Return>', lambda ev: process())
    logwin.mainloop()

def register(name, pasw):
    regwin = win("Registracija", 500, 450)

    left = Frame(regwin, 'left', pad=[5,5])

    right = Frame(regwin, 'right', '#111', wh=[280,420])
    a2 = Frame(right, 'bottom', '#4bf', 'x', False, [280, 200])
    a1 = Frame(right, 'top', '#111', 'x', False, [280,200])
    # Frame(right, 'top', '#111', 'both', False, [20,200])
    text = Label(right, fg="#bbb", bg='#333', text='Mi smo bezbedna kompanija.')
    text.pack(side = 'top', ipady=300, fill='x')

    time = 60
    quote=0
    def animate():
        nonlocal a1, a2, time, regwin, text, quote, anim
        if (time+21)//84:
            text.config(text=['Mi smo bezbedna kompanija.',"Definitivno vam ne krademo podatke.","Možete nam verovati."][quote%3])
            quote += 1
        time = (time+21)%84-20
        a1.config(height=min(450, 270-130 * math.sin(0.075 * time)))
        a2.config(height=max(0, 80 + 70 * math.sin(0.075 * time + 1.3)))
        a2.config(bg=f"#44{int(118 + 64 * math.sin(0.075 * time + math.pi/4)):02x}ff")
        anim = regwin.after(40, animate)
    anim = regwin.after(40, animate)
    right.config(bg='#444')

    un = box("Korisničko ime:", left, name, fcs=True)
    fn = box("Ime:", left)
    ln = box("Prezime:", left)
    pw1 = box("Lozinka:", left, pasw, pw=True)
    pw2 = box("Ponovi lozinku:", left, pw=True)

    def process():
        global persons
        if '|' in un.get()+fn.get()+ln.get():
            msg(regwin, 'Karakter "|" nije dozvoljen.')

        elif ' ' in un.get():
            msg(regwin, "Korisničko ime ne može sadržati razmake.")

        elif un.get() in persons:
            msg(regwin, "Korisničko ime je zauzeto.")

        elif any(char.isdigit() for char in fn.get()+ln.get()):
            msg(regwin, "Imena/prezimena ne mogu sadržati cifre.")
        
        elif not (len(pw1.get()) >= 6 and any(char.isdigit() for char in pw1.get())):
            msg(regwin, "Lozinka mora sadržati bar 6 karaktera i bar jednu cifru.")

        elif '' in {un.get(), pw1.get(), pw2.get(), fn.get().strip(), ln.get().strip()}:
            msg(regwin, "Sva polja moraju biti popunjena.")

        elif pw1.get() != pw2.get():
            msg(regwin, "Lozinke se ne poklapaju.")

        else:
            salt = os.urandom(16).hex()
            obj = Person(un.get(), hashlib.sha256((pw1.get()+salt).encode('utf-8')).hexdigest(), fn.get().strip(), ln.get().strip(), salt)
            if not obj.check():
                persons[un.get()] = obj
                save(persons, Person)
                regwin.after_cancel(anim)
                msg(regwin, "Uspešno ste se registrovali.")
                regwin.destroy()
                login(un.get(), pw1.get())
    
    Button(left, "REGISTRUJ SE >", process, 'Accent')
    Button(left, "PRIJAVA...", lambda: (
        regwin.after_cancel(anim),
        regwin.destroy(), 
        login(un.get(), pw1.get())
    ), '#331844')
    regwin.bind('<Return>', lambda ev: process())
    right.config(bg='#333')
    regwin.mainloop()
